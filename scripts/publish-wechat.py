#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号草稿发布（from-zero-tutorial）

流程（参考 weflow backend/engine/publish.py 与 api.py）：
    1. 读取 config.yaml（公众号凭据、作者、主题、mermaid 命令等）
    2. md → 微信兼容 HTML（复用 scripts/md-to-html.py）
    3. 上传正文图片（/media/uploadimg，不占永久素材）并替换 HTML 里的 src
    4. 上传封面（/material/add_material?type=thumb）拿 thumb_media_id
    5. 创建草稿（/draft/add）

用法：
    python publish-wechat.py --input "01-数学竞赛是什么.md" --dry-run   # 先干跑
    python publish-wechat.py --input "01-数学竞赛是什么.md"              # 正式发草稿
    python publish-wechat.py --input "01-数学竞赛是什么.md" --theme refined-blue --cover assets/cover-01.png

注意：
    - 公众号对正文图片用 uploadimg 接口（URL 永久有效、不占素材库配额）；
      封面用永久素材接口，每月有配额，重复发布同一封面会占用额度。
    - 缺图（引用了但上传失败）默认中止；传 --allow-missing-images 可继续。
    - --dry-run 只做本地检查，不调用微信 API。
    - 发布成功后会把草稿信息（media_id、标题、摘要、图片映射、封面 media_id 等）
      写入 <skill>/draft-records.json，供 update-wechat-draft.py 后续更新草稿使用。
"""

import argparse
import json
import re
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def _setup_console_utf8():
    """Windows 控制台默认 GBK，中文输出会报 UnicodeEncodeError；改为 UTF-8 容错输出。"""
    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_setup_console_utf8()


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = SKILL_ROOT / "config.yaml"
RECORDS_FILE = SKILL_ROOT / "draft-records.json"
API_BASE = "https://api.weixin.qq.com/cgi-bin"
_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
_IMG_SRC_RE = re.compile(r"(<img[^>]*?src=\")([^\"]+)(\")")


class PublishError(Exception):
    pass


def load_config(path=None):
    path = Path(path or DEFAULT_CONFIG)
    if not path.exists():
        raise PublishError(f"配置文件不存在：{path}")
    if yaml is None:
        raise PublishError("未安装 PyYAML，无法读取 config.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_account(config, account=None, allow_placeholder=False):
    accounts = (config.get("accounts") or {})
    name = account or (config.get("default") or "main")
    acc = accounts.get(name)
    if not acc:
        raise PublishError(f"账号不存在：{name}（accounts 里可选：{', '.join(accounts)}）")
    if not acc.get("app_id") or not acc.get("app_secret") or "你的" in str(acc.get("app_id", "")):
        if allow_placeholder:
            print("[警告] 账号尚未配置真实 AppID/AppSecret，以下仅为干跑演示。", file=sys.stderr)
            return name, acc
        raise PublishError(
            f"账号 {name} 未配置 AppID/AppSecret。请编辑 {DEFAULT_CONFIG} 填入你自己的公众号凭据。"
        )
    return name, acc


def api_call(method, url, **kwargs):
    # 微信 API 会把请求体里的 \uXXXX 转义当作字面文本存储（不解析 JSON 转义），
    # 因此必须用 ensure_ascii=False 发送 UTF-8 中文原文，否则草稿箱全是乱码。
    if "json" in kwargs and "data" not in kwargs:
        payload = kwargs.pop("json")
        kwargs["data"] = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = dict(kwargs.get("headers") or {})
        headers.setdefault("Content-Type", "application/json; charset=utf-8")
        kwargs["headers"] = headers
    try:
        resp = requests.request(method, url, timeout=30, **kwargs)
        data = resp.json()
    except Exception as e:
        # 异常文本可能包含完整请求 URL（urllib3 会把 secret 带进报错），同样脱敏
        detail = re.sub(r"(secret|appsecret)=[^&\s\"']+", r"\1=***", str(e))
        raise PublishError(f"微信 API 请求失败：{_mask_url(url)} -> {detail}")
    if data.get("errcode", 0) not in (0, None):
        raise PublishError(f"微信 API 错误 {data.get('errcode')}: {data.get('errmsg')}（{_mask_url(url)}）")
    return data


def _mask_url(url):
    """脱敏：隐藏 URL 查询参数里的 secret / appsecret，避免密钥进日志。"""
    return re.sub(r"(secret|appsecret)=[^&]+", r"\1=***", url)


def get_access_token(app_id, app_secret):
    url = f"{API_BASE}/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    data = api_call("GET", url)
    return data["access_token"]


def upload_content_image(token, image_path):
    """正文图片：/media/uploadimg，返回永久可用的 url。"""
    url = f"{API_BASE}/media/uploadimg?access_token={token}"
    with open(image_path, "rb") as f:
        data = api_call("POST", url, files={"media": (image_path.name, f)})
    return data["url"]


def upload_thumb(token, image_path):
    """封面：/material/add_material?type=thumb，返回 thumb_media_id（占永久素材额度）。"""
    url = f"{API_BASE}/material/add_material?access_token={token}&type=thumb"
    with open(image_path, "rb") as f:
        data = api_call("POST", url, files={"media": (image_path.name, f)})
    return data["media_id"]


def add_draft(token, article):
    url = f"{API_BASE}/draft/add?access_token={token}"
    data = api_call("POST", url, json={"articles": [article]})
    return data["media_id"]


# ============================================================
# 草稿记录（draft-records.json）：发布后留存，供更新草稿脚本使用
# ============================================================

def load_records(records_path=None):
    path = Path(records_path or RECORDS_FILE)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_records(records, records_path=None):
    path = Path(records_path or RECORDS_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def record_draft(records, media_id, **fields):
    """按 media_id 写入/更新一条草稿记录。"""
    record = {"media_id": media_id, **fields}
    for i, r in enumerate(records):
        if r.get("media_id") == media_id:
            records[i] = record
            return record
    records.append(record)
    return record


def extract_local_images(md_text, base_dir):
    """从 md 提取本地图片路径（去重、保留顺序、排除 http）。"""
    seen, result = set(), []
    for m in _IMG_RE.finditer(md_text):
        src = m.group(2).strip()
        if src.startswith(("http://", "https://", "data:")):
            continue
        p = Path(src)
        if not p.is_absolute():
            p = Path(base_dir) / p
        p = p.resolve()
        if p.exists() and str(p) not in seen:
            seen.add(str(p))
            result.append(p)
    return result


def _to_rel(p, base_dir):
    """路径转为相对 base_dir 的 posix 路径（记录里不存绝对路径，便于换机器迁移）。"""
    try:
        return Path(p).resolve().relative_to(Path(base_dir).resolve()).as_posix()
    except (ValueError, OSError):
        return str(p)


def png_size(path):
    """读取 PNG 宽高（IHDR 头）；非 PNG 返回 None。"""
    try:
        with open(path, "rb") as f:
            head = f.read(24)
    except OSError:
        return None
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def check_cover_ratio(cover_path, tolerance=0.2):
    """检查封面宽高比是否接近微信 2.35:1；返回 (size, warning)。"""
    size = png_size(cover_path)
    if size is None:
        return None, "封面不是 PNG，无法检查宽高比"
    w, h = size
    ratio = w / h
    if abs(ratio - 2.35) > tolerance:
        msg = (
            f"封面宽高比 {ratio:.2f}:1（{w}×{h}），偏离微信头条封面 2.35:1；"
            "微信将按 2.35:1 从中心裁切，左右边缘的文字可能被截断。"
            "请用 generate.mjs --width 1068 --height 455 重新生成封面，"
            "或用 --cover 指定合规封面（--allow-off-ratio-cover 可强制继续）"
        )
        return (w, h, ratio), msg
    return (w, h, ratio), None


def replace_image_srcs(html_text, mapping):
    """mapping: {原 md 相对路径字符串: CDN url}，替换 HTML 中出现的 src。

    HTML 里的 src 可能与 mapping key 写法不同（如 ./assets/x.png、
    ../assets/x.png、Windows 反斜杠），先规范化再匹配，避免替换失败
    导致发布后微信端图片断链。
    """
    if not mapping:
        return html_text
    norm = {}
    for orig, url in mapping.items():
        key = orig.replace("\\", "/").strip()
        while key.startswith("./"):
            key = key[2:]
        norm[key] = url

    def repl(m):
        src = m.group(2).strip()
        key = src.replace("\\", "/")
        while key.startswith("./"):
            key = key[2:]
        url = norm.get(key)
        return m.group(1) + (url if url else src) + m.group(3)

    return _IMG_SRC_RE.sub(repl, html_text)


def _load_md_to_html():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "md_to_html", Path(__file__).resolve().parent / "md-to-html.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_article(md_path, html_path, theme, title, digest, cover_path,
                  html_dir="html", mermaid_cmd="mmdc", for_publish=True, dry_run=False):
    """复用 md-to-html 生成 HTML，返回 (content_html, meta)。"""
    md_to_html = _load_md_to_html()
    _, meta = md_to_html.convert_article(
        md_path, out_path=html_path, theme_arg=theme, html_dir=html_dir,
        mermaid_cmd=mermaid_cmd,
        for_publish=for_publish, dry_run=False,
    )
    html_text = html_path.read_text(encoding="utf-8")
    # 取出 <body> 内容（微信草稿只认内容 HTML）
    m = re.search(r"<body[^>]*>(.*)</body>", html_text, re.DOTALL)
    content = m.group(1) if m else html_text
    if not title:
        title = meta["title"]
    if not digest:
        digest = meta["digest"]
    return content, meta


def main():
    parser = argparse.ArgumentParser(description="发布文章到微信公众号草稿箱（from-zero-tutorial）")
    parser.add_argument("--input", "-i", help="文章 Markdown 路径（与 --html 二选一）")
    parser.add_argument("--html", help="已生成的 HTML 路径（跳过 md→HTML，图片仍会上传替换）")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="config.yaml 路径")
    parser.add_argument("--account", help="账号名（config.yaml accounts 里的键，默认 default）")
    parser.add_argument("--theme", help="HTML 主题 slug（themes/*.json；缺省随机）")
    parser.add_argument("--html-dir", default="html", help="HTML 输出目录（相对文章目录，默认 html）")
    parser.add_argument("--mermaid-cmd", default="mmdc", help="mermaid 渲染命令（默认 mmdc，找不到则发布会中止）")
    parser.add_argument("--title", help="标题（缺省从文章提取）")
    parser.add_argument("--digest", help="摘要（缺省从文章提取）")
    parser.add_argument("--cover", help="封面图路径（缺省用 frontmatter cover 或文章第一张图）")
    parser.add_argument("--allow-off-ratio-cover", action="store_true", help="封面宽高比偏离 2.35:1 时仍继续发布")
    parser.add_argument("--dry-run", action="store_true", help="只做本地检查，不调用微信 API")
    parser.add_argument("--allow-missing-images", action="store_true", help="缺图仍继续发布")
    parser.add_argument("--duplicate-ok", action="store_true", help="已存在同标题草稿记录时仍新建草稿（默认中止，建议改用 update-wechat-draft.py）")
    args = parser.parse_args()

    if not args.input and not args.html:
        parser.error("必须提供 --input <md> 或 --html <html>")

    config = load_config(args.config)
    account_name, account = get_account(config, args.account, allow_placeholder=args.dry_run)
    author = account.get("author") or ""
    publish_cfg = config.get("publish") or {}
    allow_missing = args.allow_missing_images or bool(
        publish_cfg.get("allow_missing_images", False)
    )
    # 留言设置（微信草稿接口字段）：打开留言 + 所有人可留言为默认
    need_open_comment = 1 if publish_cfg.get("need_open_comment", True) else 0
    only_fans_can_comment = 1 if publish_cfg.get("only_fans_can_comment", False) else 0

    # ── 1. 生成/读取 HTML ──
    temp_html = None
    if args.html:
        html_path = Path(args.html)
        if not html_path.exists():
            parser.error(f"HTML 不存在：{html_path}")
        content = html_path.read_text(encoding="utf-8")
        m = re.search(r"<body[^>]*>(.*)</body>", content, re.DOTALL)
        content = m.group(1) if m else content
        md_path = None
        base_dir = html_path.parent
        cover = args.cover or ""
        title = args.title or ""
        digest = args.digest or ""
    else:
        md_path = Path(args.input)
        if not md_path.exists():
            parser.error(f"文章不存在：{md_path}")
        html_path = md_path.parent / args.html_dir / f"{md_path.stem}.html"
        base_dir = md_path.parent
        content, meta = build_article(
            md_path, html_path, args.theme, args.title, args.digest, args.cover,
            html_dir=args.html_dir, mermaid_cmd=args.mermaid_cmd,
            for_publish=True, dry_run=False,
        )
        cover = args.cover or meta.get("cover") or ""
        title = args.title or meta["title"]
        digest = args.digest or meta["digest"]
        temp_html = html_path

    # ── 2. 收集正文图片（md 里引用的本地图片）──
    local_images = []
    if md_path is not None:
        local_images = extract_local_images(md_path.read_text(encoding="utf-8"), base_dir)
    else:
        for m in _IMG_SRC_RE.finditer(content):
            src = m.group(2)
            if src.startswith(("http://", "https://", "data:")):
                continue
            p = Path(src)
            if not p.is_absolute():
                p = Path(base_dir) / p
            if p.exists():
                local_images.append(p.resolve())
    local_images = list(dict.fromkeys(local_images))

    # 封面路径解析（相对 md/html 所在目录）
    cover_path = None
    if cover:
        cp = Path(cover)
        if not cp.is_absolute():
            cp = Path(base_dir) / cp
        if cp.exists():
            cover_path = cp.resolve()
        else:
            raise PublishError(f"封面图不存在：{cover}")
    if cover_path is None and local_images:
        cover_path = local_images[0]

    print(f"[账号] {account_name}（{account.get('name', '')}）")
    print(f"[标题] {title}")
    # 防重复发布：已存在同标题草稿记录时提示（正式发布默认中止，避免草稿箱堆积重复）
    records = load_records()
    dup = next((r for r in records if r.get("title") == title), None)
    if dup:
        dup_msg = (
            f"已存在同标题草稿记录（media_id={dup['media_id']}，发布于 {dup.get('published_at') or '未知'}）。"
            "请改用 update-wechat-draft.py --key/--media-id 更新，避免微信草稿箱出现重复草稿；"
            "确认要另建一条草稿请加 --duplicate-ok。"
        )
        if args.dry_run:
            print(f"[警告] {dup_msg}", file=sys.stderr)
        elif not args.duplicate_ok:
            raise PublishError(dup_msg)
        else:
            print(f"[警告] {dup_msg}", file=sys.stderr)
    print(f"[摘要] {digest[:50]}")
    print(f"[作者] {author or '（未配置）'}")
    print(f"[正文图] {len(local_images)} 张")
    for i, p in enumerate(local_images, 1):
        print(f"   {i}. {p.relative_to(base_dir)}")
    print(f"[封面] {cover_path.relative_to(base_dir) if cover_path else '（无）'}")
    cover_size, cover_warning = (None, None)
    if cover_path:
        cover_size, cover_warning = check_cover_ratio(cover_path)
        if cover_size:
            w, h, ratio = cover_size
            print(f"[封面比例] {w}×{h}（{ratio:.2f}:1，微信要求 2.35:1）")
        if cover_warning:
            if args.dry_run or args.allow_off_ratio_cover:
                print(f"[警告] {cover_warning}", file=sys.stderr)
            else:
                raise PublishError(cover_warning)
    print(f"[留言] 打开={'是' if need_open_comment else '否'}，仅粉丝可留言={'是' if only_fans_can_comment else '否'}")
    print(f"[HTML] {len(content)} 字符")

    # 微信草稿标题限制 64 字节（中文约 20 字），超长先拦截，避免浪费上传
    title_bytes = len(title.encode("utf-8"))
    if title_bytes > 64:
        msg = f"标题超长：{title_bytes} 字节 > 64（微信限制），请用 --title 提供更短标题（建议 ≤20 字）"
        if args.dry_run:
            print(f"[警告] {msg}")
        else:
            raise PublishError(msg)

    if args.dry_run:
        print("\n[干跑] 未调用微信 API。正式发布将依次执行：")
        print("   1. GET /token（获取 access_token）")
        if local_images:
            print(f"   2. POST /media/uploadimg × {len(local_images)}（上传正文图，替换 HTML src）")
        if cover_path:
            print("   3. POST /material/add_material?type=thumb（上传封面 → thumb_media_id）")
        print("   4. POST /draft/add（创建草稿，返回 media_id）")
        return

    # ── 3. 调微信 API ──
    token = get_access_token(account["app_id"], account["app_secret"])
    print("\n[1/4] access_token 获取成功")

    mapping = {}
    for i, img in enumerate(local_images, 1):
        try:
            url = upload_content_image(token, img)
            orig = img.relative_to(base_dir).as_posix()
            mapping[orig] = url
            print(f"[2/4] 正文图 {i}/{len(local_images)} 上传成功：{img.name}")
        except Exception as e:
            print(f"[错误] 正文图上传失败：{img.name} -> {e}", file=sys.stderr)
            if not allow_missing:
                raise PublishError(f"{len(local_images) - len(mapping)} 张图未上传，发布中止（--allow-missing-images 可跳过）")
    content = replace_image_srcs(content, mapping)

    thumb_media_id = None
    if cover_path:
        try:
            thumb_media_id = upload_thumb(token, cover_path)
            print(f"[3/4] 封面上传成功：{cover_path.name} -> {thumb_media_id}")
        except Exception as e:
            raise PublishError(f"封面上传失败：{e}")
    else:
        print("[3/4] 无封面，草稿将使用默认封面（建议用 --cover 指定）")

    article = {
        "title": title,
        "author": author or "未署名",
        "digest": digest,
        "content": content,
        "content_source_url": "",
        "need_open_comment": need_open_comment,
        "only_fans_can_comment": only_fans_can_comment,
    }
    if thumb_media_id:
        article["thumb_media_id"] = thumb_media_id
    media_id = add_draft(token, article)
    print(f"[4/4] 草稿创建成功 media_id={media_id}")
    if need_open_comment:
        print("[提醒] 留言已打开；「自动精选留言」无公开 API，请到公众号后台人工开启：功能/互动 → 留言管理 → 自动精选")

    # 发布成功后记录草稿信息，便于后续 update-wechat-draft.py 更新
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    records = load_records()
    record_draft(
        records,
        media_id,
        title=title,
        digest=digest,
        author=author or "",
        account=account_name,
        published_at=now,
        updated_at=now,
        md_path=_to_rel(md_path, base_dir) if md_path else "",
        html_path=_to_rel(html_path, base_dir),
        base_dir=str(base_dir),
        cover_path=_to_rel(cover_path, base_dir) if cover_path else "",
        thumb_media_id=thumb_media_id or "",
        image_mapping=mapping,
        local_images=[_to_rel(p, base_dir) for p in local_images],
    )
    save_records(records)
    print(f"[记录] 草稿信息已写入 {RECORDS_FILE.name}")

    # 回写文章 frontmatter：status 阶段标记 + 发布信息（与草稿记录同步）
    if md_path is not None:
        try:
            _load_md_to_html().update_frontmatter(
                md_path,
                status_add="已发布草稿",
                published_at=datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                wechat_media_id=media_id,
                wechat_title=title,
                wechat_digest=digest,
                wechat_images=len(mapping),
            )
            print(f"[记录] 发布信息已回写 {md_path.name} frontmatter")
        except Exception as e:
            print(f"[警告] frontmatter 回写失败：{e}", file=sys.stderr)

    print(json.dumps({"media_id": media_id, "title": title, "images": len(mapping)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
