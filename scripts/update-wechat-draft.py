#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新微信公众号草稿（from-zero-tutorial）

配合 publish-wechat.py 使用：发布时会把草稿信息写入 <skill>/draft-records.json，
本脚本按记录定位草稿，重新生成/读取正文、复用已上传的图片 URL、更新标题/摘要/正文，
调用 /draft/update 重写草稿，并刷新记录。

用法：
    python update-wechat-draft.py --list                     # 列出已发布的草稿记录
    python update-wechat-draft.py --key 别急着入坑            # 按标题关键词定位并更新
    python update-wechat-draft.py --media-id <id>            # 按 media_id 更新（无记录时拉取草稿内容并修复 \\uXXXX 乱码）
    python update-wechat-draft.py --key 别急着入坑 --title "新标题" --digest "新摘要"
    python update-wechat-draft.py --key 03 --input "03-别急着入坑.md" --theme refined-blue
    python update-wechat-draft.py --key 03 --cover assets/cover-03.png   # 换封面

注意：
    - 正文图片优先复用记录里已上传的 CDN URL（不重复占上传额度）；新出现的本地图才重新上传；
    - 封面默认复用原 thumb_media_id；--cover 指定新封面才重新上传；
    - 无记录且只给 --media-id 时，会拉取草稿现有内容并把 \\uXXXX 乱码解码后重写（修复场景）。
"""

import argparse
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests


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

# 复用 publish-wechat.py 里的公共函数（load_config / get_account / 上传 / 记录读写）
_spec = importlib.util.spec_from_file_location(
    "publish_wechat", Path(__file__).resolve().parent / "publish-wechat.py"
)
pw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pw)


UNICODE_ESC = re.compile(r"(?<!\\)\\u([0-9a-fA-F]{4})")
_IMG_SRC_RE = re.compile(r"(<img[^>]*?src=\")([^\"]+)(\")")


def decode_unicode_escapes(text):
    """把 \\uXXXX 转义序列还原为真实字符（修复发布时被转义的草稿）。"""
    if not text:
        return text
    return UNICODE_ESC.sub(lambda m: chr(int(m.group(1), 16)), text)


def has_unicode_escapes(text):
    return bool(UNICODE_ESC.search(text or ""))


def extract_body(html_text):
    m = re.search(r"<body[^>]*>(.*)</body>", html_text, re.DOTALL)
    return m.group(1) if m else html_text


def build_content_from_md(md_path, html_path, theme, html_dir="html", mermaid_cmd="mmdc"):
    """用 md-to-html 重新生成正文 HTML（与发布脚本同一套逻辑）。"""
    spec = importlib.util.spec_from_file_location(
        "md_to_html", Path(__file__).resolve().parent / "md-to-html.py"
    )
    md_to_html = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(md_to_html)
    _, meta = md_to_html.convert_article(
        md_path, out_path=html_path, theme_arg=theme, html_dir=html_dir,
        mermaid_cmd=mermaid_cmd, for_publish=True, dry_run=False,
    )
    content = extract_body(html_path.read_text(encoding="utf-8"))
    return content, meta


def find_records(records, media_id=None, key=None):
    """返回所有匹配的记录（key 按标题/文章路径/media_id 匹配）。"""
    if media_id:
        return [r for r in records if r.get("media_id") == media_id]
    if key:
        k = key.lower()
        return [
            r for r in records
            if k in " ".join([
                str(r.get("title", "")),
                str(r.get("md_path", "")),
                str(r.get("media_id", "")),
            ]).lower()
        ]
    return []


def resolve_record_path(record, key):
    """把记录里的相对路径按 base_dir 解析为绝对路径（记录统一存相对路径）。"""
    raw = (record or {}).get(key) or ""
    if not raw:
        return None
    p = Path(raw)
    if not p.is_absolute():
        p = Path(record.get("base_dir") or Path.cwd()) / p
    return p


def list_records(records):
    if not records:
        print("暂无草稿记录。发布后记录会自动写入 draft-records.json。")
        return
    print(f"共 {len(records)} 条草稿记录（{RECORDS_FILE.name}）：")
    for i, r in enumerate(records, 1):
        print(f"{i}. media_id={r.get('media_id')}")
        print(f"   标题: {r.get('title', '')}")
        print(f"   账号: {r.get('account', '')} | 发布: {r.get('published_at', '')} | 更新: {r.get('updated_at', '')}")
        print(f"   文章: {r.get('md_path') or r.get('html_path') or '（仅 media_id）'}")


def collect_local_srcs(content):
    """收集正文 HTML 中引用的本地图片路径（相对 base_dir 解析）。"""
    result = []
    for m in _IMG_SRC_RE.finditer(content):
        src = m.group(2).strip()
        if src.startswith(("http://", "https://", "data:")):
            continue
        result.append(src)
    return list(dict.fromkeys(result))


def resolve_local_image(src, base_dir):
    """按多个候选目录解析本地图片路径（兼容 html 在 html/ 子目录、图片在文章根目录的情况）。"""
    direct = Path(src)
    if direct.is_absolute():
        return direct if direct.exists() else None
    candidates = [direct, Path(base_dir) / src, Path(base_dir).parent / src]
    for c in candidates:
        if c.exists():
            return c
    return None


def main():
    parser = argparse.ArgumentParser(description="更新微信公众号草稿（from-zero-tutorial）")
    parser.add_argument("--list", action="store_true", help="列出草稿记录")
    parser.add_argument("--media-id", help="草稿 media_id（优先；无记录时会拉草稿内容并修复乱码）")
    parser.add_argument("--key", help="在记录里按标题/文章路径关键词定位草稿")
    parser.add_argument("--input", "-i", help="文章 Markdown 路径（可选，重新生成正文）")
    parser.add_argument("--html", help="已生成的 HTML 路径（可选，跳过 md→HTML）")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="config.yaml 路径")
    parser.add_argument("--account", help="账号名（默认用记录里的账号或 config default）")
    parser.add_argument("--theme", help="HTML 主题 slug（重新生成时用）")
    parser.add_argument("--html-dir", default="html", help="HTML 输出目录（默认 html）")
    parser.add_argument("--mermaid-cmd", default="mmdc", help="mermaid 渲染命令")
    parser.add_argument("--title", help="覆盖标题")
    parser.add_argument("--digest", help="覆盖摘要")
    parser.add_argument("--author", help="覆盖作者")
    parser.add_argument("--cover", help="更换封面图（重新上传为 thumb 素材）")
    parser.add_argument("--allow-missing-images", action="store_true", help="新图上传失败仍继续")
    args = parser.parse_args()

    config = pw.load_config(args.config)
    records = pw.load_records()
    publish_cfg = config.get("publish") or {}
    need_open_comment = 1 if publish_cfg.get("need_open_comment", True) else 0
    only_fans_can_comment = 1 if publish_cfg.get("only_fans_can_comment", False) else 0

    if args.list:
        list_records(records)
        return

    if args.media_id is None and args.key is None:
        parser.error("必须提供 --media-id 或 --key（--list 可查看记录）")
    matches = find_records(records, media_id=args.media_id, key=args.key)
    if len(matches) > 1:
        print("--key 匹配到多条草稿记录，为避免更新错草稿，请用 --media-id 精确定位：")
        for r in matches:
            print(f"  media_id={r.get('media_id')} | 标题: {r.get('title', '')} | 发布: {r.get('published_at', '')}")
        parser.error(f"匹配到 {len(matches)} 条记录，需指定 --media-id")
    record = matches[0] if matches else None
    if record is None and args.key:
        parser.error(f"记录中未找到匹配“{args.key}”的草稿（可先用 --list 查看记录，或改用 --media-id 直接定位）")

    # ── 1. 确定账号 ──
    account_name = args.account or (record or {}).get("account") or None
    account_name, account = pw.get_account(config, account_name)

    # ── 2. 构建正文 ──
    token = None
    base_dir = Path((record or {}).get("base_dir") or Path.cwd())
    temp_html = None
    if args.input:
        md_path = Path(args.input)
        if not md_path.exists():
            parser.error(f"文章不存在：{md_path}")
        html_path = md_path.parent / args.html_dir / f"{md_path.stem}.html"
        base_dir = md_path.parent
        content, meta = build_content_from_md(
            md_path, html_path, args.theme, html_dir=args.html_dir, mermaid_cmd=args.mermaid_cmd,
        )
        # 更新草稿时默认沿用发布时的标题（记录里的短标题，微信限 64 字节），
        # 不要用 frontmatter 完整长标题覆盖；显式 --title 才替换。
        title = args.title or (record or {}).get("title") or meta["title"]
        digest = args.digest or meta["digest"]
        author = args.author or account.get("author") or ""
        temp_html = html_path
    elif args.html:
        html_path = Path(args.html)
        if not html_path.exists():
            parser.error(f"HTML 不存在：{html_path}")
        content = extract_body(html_path.read_text(encoding="utf-8"))
        base_dir = html_path.parent
        title = args.title or (record or {}).get("title") or ""
        digest = args.digest or (record or {}).get("digest") or ""
        author = args.author or account.get("author") or (record or {}).get("author") or ""
    elif record and record.get("html_path"):
        html_path = resolve_record_path(record, "html_path")
        if html_path is not None and html_path.exists():
            content = extract_body(html_path.read_text(encoding="utf-8"))
            title = args.title or record.get("title") or ""
            digest = args.digest or record.get("digest") or ""
            author = args.author or record.get("author") or account.get("author") or ""
        else:
            raise pw.PublishError(f"记录中的 HTML 不存在：{html_path}（可用 --input/--html 重新生成）")
    else:
        # 无记录/无本地文件：拉取草稿现有内容并解码 \uXXXX（修复乱码场景）
        token = pw.get_access_token(account["app_id"], account["app_secret"])
        target_media_id = args.media_id or (record or {}).get("media_id")
        if not target_media_id:
            raise pw.PublishError("无法确定 media_id（请用 --media-id）")
        data = pw.api_call(
            "POST", f"{API_BASE}/draft/get?access_token={token}",
            json={"media_id": target_media_id},
        )
        item = data["news_item"][0]
        content = decode_unicode_escapes(item.get("content", ""))
        title = args.title or decode_unicode_escapes(item.get("title", ""))
        digest = args.digest or decode_unicode_escapes(item.get("digest", ""))
        author = args.author or decode_unicode_escapes(item.get("author", "")) or account.get("author") or ""

    # ── 3. 图片：复用记录中的 CDN URL，新图上传 ──
    mapping = dict((record or {}).get("image_mapping") or {})
    content = pw.replace_image_srcs(content, mapping)  # 先替换已上传的

    if token is None:
        token = pw.get_access_token(account["app_id"], account["app_secret"])
    print(f"[账号] {account_name}（{account.get('name', '')}）")
    print(f"[标题] {title}")
    print(f"[摘要] {digest[:50]}")
    print(f"[正文] {len(content)} 字符")

    allow_missing = args.allow_missing_images or bool((config.get("publish") or {}).get("allow_missing_images", False))
    missing = []
    for src in collect_local_srcs(content):
        if src in mapping:
            continue
        p = resolve_local_image(src, base_dir)
        if p is None:
            missing.append(src)
            print(f"[警告] 本地图片不存在：{src}", file=sys.stderr)
            continue
        try:
            url = pw.upload_content_image(token, p)
            mapping[src] = url
            content = content.replace(f'"{src}"', f'"{url}"')
            print(f"[图片] 新上传：{src}")
        except Exception as e:
            print(f"[错误] 图片上传失败：{src} -> {e}", file=sys.stderr)
            missing.append(src)
    if missing and not allow_missing:
        raise pw.PublishError(f"{len(missing)} 张图未处理，更新中止（--allow-missing-images 可跳过）")

    # ── 4. 封面 ──
    thumb_media_id = (record or {}).get("thumb_media_id") or ""
    if args.cover:
        cover_path = Path(args.cover)
        if not cover_path.is_absolute():
            cover_path = Path(base_dir) / cover_path
        if not cover_path.exists():
            parser.error(f"封面不存在：{cover_path}")
        thumb_media_id = pw.upload_thumb(token, cover_path)
        print(f"[封面] 已上传新封面：{cover_path.name} -> {thumb_media_id}")

    # ── 5. 更新草稿 ──
    media_id = args.media_id or (record or {}).get("media_id")
    if not media_id:
        raise pw.PublishError("无法确定 media_id（请用 --media-id 或确保记录存在）")
    title_bytes = len(title.encode("utf-8"))
    if title_bytes > 64:
        raise pw.PublishError(
            f"标题超长：{title_bytes} 字节 > 64（微信限制），请用 --title 提供更短标题（建议 ≤20 字）"
        )
    # 微信 draft/update 必须携带 thumb_media_id，缺失会报 40007 invalid media_id
    if not thumb_media_id:
        data = pw.api_call(
            "POST", f"{API_BASE}/draft/get?access_token={token}",
            json={"media_id": media_id},
        )
        thumb_media_id = data["news_item"][0].get("thumb_media_id", "")
        print(f"[封面] 复用草稿原封面：{thumb_media_id}")
    update_articles = {
        "title": title,
        "author": author or "未署名",
        "digest": digest,
        "content": content,
        "show_cover_pic": 0,
        "need_open_comment": need_open_comment,
        "only_fans_can_comment": only_fans_can_comment,
    }
    if thumb_media_id:
        update_articles["thumb_media_id"] = thumb_media_id
    result = pw.api_call(
        "POST", f"{API_BASE}/draft/update?access_token={token}",
        json={"media_id": media_id, "index": 0, "articles": update_articles},
    )
    print(f"[更新] draft/update 结果：{result}")

    # ── 6. 刷新记录并验证 ──
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    record = pw.record_draft(
        records,
        media_id,
        title=title,
        digest=digest,
        author=author or "",
        account=account_name,
        published_at=(record or {}).get("published_at") or now,
        updated_at=now,
        md_path=pw._to_rel(Path(args.input), base_dir) if args.input else (record or {}).get("md_path", ""),
        html_path=pw._to_rel(Path(args.html), base_dir) if args.html else (record or {}).get("html_path", ""),
        base_dir=str(base_dir.resolve()),
        cover_path=pw._to_rel(Path(args.cover), base_dir) if args.cover else (record or {}).get("cover_path", ""),
        thumb_media_id=thumb_media_id,
        image_mapping=mapping,
        local_images=(record or {}).get("local_images", []),
    )
    pw.save_records(records)
    print(f"[记录] 草稿记录已刷新（{RECORDS_FILE.name}）")

    check = pw.api_call(
        "POST", f"{API_BASE}/draft/get?access_token={token}",
        json={"media_id": media_id},
    )
    item = check["news_item"][0]
    c = item.get("content", "")
    esc = has_unicode_escapes(item.get("title", "")) or has_unicode_escapes(item.get("digest", "")) or has_unicode_escapes(c)
    print("\n[验证]")
    print("  标题:", item.get("title"))
    print("  摘要:", item.get("digest"))
    print(f"  正文: {len(c)} 字符，含 \\uXXXX 乱码: {esc}")
    if esc:
        print("  [警告] 草稿仍含 \\uXXXX 转义，请检查内容来源。", file=sys.stderr)


if __name__ == "__main__":
    main()
