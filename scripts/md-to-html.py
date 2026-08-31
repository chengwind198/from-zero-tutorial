#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md → HTML 转换器（from-zero-tutorial）

把系列文章（Obsidian Markdown）转成微信兼容、带主题排版的 HTML。
微信编辑器要求所有样式内联，本脚本产出的 HTML 同时可在浏览器直接预览。

用法：
    python md-to-html.py --input "01-数学竞赛是什么.md" --theme refined-blue
    python md-to-html.py --input "01-数学竞赛是什么.md"            # 未指定主题 → 随机
    python md-to-html.py --input "01-数学竞赛是什么.md" --dry-run   # 只打印将用主题/输出路径

主题：
    - themes/*.json（15 套，格式与 weflow 一致）
    - 选择顺序：--theme 指定 > 随机

Markdown → HTML 核心使用第三方库 python-markdown
（GitHub Python-Markdown/markdown，Python 生态 star 最高的实现，约 4.2k）：
表格 / 围栏代码块 / 有序列表由库解析，高亮标记（==、++、%%、&&、!!、@@、^^）
通过库的 InlineProcessor 扩展实现；主题内联样式由本脚本套用（微信要求内联）。

Mermaid：
    微信公众号不支持 Mermaid，发布前必须渲染成 PNG。
    - 配了 --mermaid-cmd（如 mmdc）：自动渲染并替换为 <img>
    - 没配：--for-publish 时中止（缺图不发）；普通转 HTML 时保留源码占位并警告

依赖：Python 3 + pip install markdown beautifulsoup4（pyyaml 可选，用于 frontmatter 解析）
（本脚本不读取 config.yaml、不依赖 weflow 等外部项目；主题格式与 weflow 兼容）
"""

import argparse
import json
import random
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

SKILL_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = SKILL_ROOT / "themes"

_MERMAID_RE = re.compile(r"^```mermaid\s*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


# ============================================================
# 配置与主题
# ============================================================

def list_themes():
    return sorted(p.stem for p in THEMES_DIR.glob("*.json")) if THEMES_DIR.exists() else []


def load_theme_json(slug):
    p = THEMES_DIR / f"{slug}.json"
    if not p.exists():
        raise FileNotFoundError(f"主题不存在：{slug}（可用：{', '.join(list_themes())}）")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_theme(theme_arg=None):
    if theme_arg:
        return theme_arg
    themes = list_themes()
    if not themes:
        raise FileNotFoundError(f"themes 目录为空：{THEMES_DIR}")
    return random.choice(themes)


# ============================================================
# Markdown 前置处理
# ============================================================

def parse_frontmatter(md_text):
    """剥离 YAML front matter，返回 (fm dict, body)。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", md_text, re.DOTALL)
    if not m:
        return {}, md_text
    fm_text, body = m.group(1), md_text[m.end():]
    if yaml is not None:
        try:
            fm = yaml.safe_load(fm_text) or {}
            return (fm if isinstance(fm, dict) else {}), body
        except Exception:
            pass
    # 极简 fallback：只认 title: / subtitle: / cover: 单值行
    fm = {}
    for line in fm_text.splitlines():
        kv = re.match(r"^([A-Za-z_]+):\s*(.*?)\s*$", line)
        if kv:
            fm[kv.group(1)] = kv.group(2)
    return fm, body


def _parse_status(raw):
    raw = (raw or "").strip()
    if raw.startswith("["):
        return [x.strip() for x in raw.strip("[]").split(",") if x.strip()]
    return [raw] if raw else []


def _fmt_status(value):
    if isinstance(value, (list, tuple)):
        return "[{}]".format(", ".join(str(x) for x in value))
    return str(value)


def _yaml_scalar(value):
    s = str(value)
    if re.fullmatch(r"-?\d+(\.\d+)?|true|false|null", s, re.IGNORECASE):
        return s
    return "'" + s.replace("'", "''") + "'"


def update_frontmatter(md_path, status_add=None, **fields):
    """更新文章 frontmatter：status 追加阶段标记（去重），并写入/更新指定字段。

    - status_add：追加一个阶段标记（如 "已生成html" / "已发布草稿"），自动去重；
    - fields 里传 status=... 可整体替换 status（list 或 str）；
    - 其余字段按 key: value 更新或插入（字符串值自动加引号，保证 YAML 可读）。
    返回 True 表示有改动；无 frontmatter 返回 False。
    """
    md_path = Path(md_path)
    if not md_path.exists():
        return False
    text = md_path.read_text(encoding="utf-8")
    m = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n?)", text, re.DOTALL)
    if not m:
        return False
    head, fm, tail = m.group(1), m.group(2), m.group(3)
    lines = fm.split("\n")

    def find_idx(key):
        for i, line in enumerate(lines):
            if re.match(rf"^{re.escape(key)}\s*:", line):
                return i
        return None

    def set_line(key, value):
        line = f"{key}: {_yaml_scalar(value)}"
        idx = find_idx(key)
        if idx is None:
            lines.append(line)
        else:
            lines[idx] = line

    if "status" in fields:
        val = _fmt_status(fields.pop("status"))
        idx = find_idx("status")
        if idx is None:
            lines.append(f"status: {val}")
        else:
            lines[idx] = f"status: {val}"
    if status_add:
        idx = find_idx("status")
        if idx is None:
            lines.append(f"status: [{status_add}]")
        else:
            vals = _parse_status(lines[idx].split(":", 1)[1])
            if status_add not in vals:
                vals.append(status_add)
            lines[idx] = f"status: [{', '.join(vals)}]"
    for key, value in fields.items():
        if value is not None:
            set_line(key, value)

    rest = text[m.end():]  # frontmatter 之后的正文必须原样保留
    md_path.write_text(head + "\n".join(lines) + tail + rest, encoding="utf-8")
    return True


def strip_inline_markers(text):
    """剥离行内排版标记（** == ++ 等），用于摘要/标题。"""
    for pat in [r"\*\*([^\n]+?)\*\*", r"==([^\n]+?)==", r"\+\+([^\n]+?)\+\+",
                r"%%([^\n]+?)%%", r"&&([^\n]+?)&&", r"!!([^\n]+?)!!",
                r"@@([^\n]+?)@@", r"\^\^([^\n]+?)\^\^", r"\*([^*\n]+)\*"]:
        text = re.sub(pat, r"\1", text)
    return text.replace("`", "")


def extract_title(fm, body):
    if fm.get("title"):
        return strip_inline_markers(str(fm["title"]).strip())
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if m:
        return strip_inline_markers(m.group(1).strip())
    return "未命名文章"


def extract_digest(fm, body):
    if fm.get("subtitle"):
        return strip_inline_markers(str(fm["subtitle"]).strip())[:120]
    m = re.search(r"^>\s+(.+)$", body, re.MULTILINE)
    if m:
        return strip_inline_markers(m.group(1).strip())[:120]
    text = re.sub(r"^#+\s*", "", body, flags=re.MULTILINE)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = strip_inline_markers(" ".join(text.split()))
    return text[:120]


# ============================================================
# Mermaid 渲染
# ============================================================

def render_mermaid_blocks(body, base_dir, out_html_path, mermaid_cmd, for_publish):
    """渲染 ```mermaid 块为 PNG；返回 (新 body, 未渲染数, 警告列表)。"""
    blocks = list(_MERMAID_RE.finditer(body))
    if not blocks:
        return body, 0, []
    warnings = []
    unrendered = 0
    out_dir = out_html_path.parent
    for i, m in enumerate(blocks, 1):
        code = m.group(1).strip()
        png = out_dir / f"mermaid-{i:02d}.png"
        if mermaid_cmd:
            try:
                tmp = out_dir / f"mermaid-{i:02d}.mmd"
                tmp.write_text(code, encoding="utf-8")
                subprocess.run(
                    [mermaid_cmd, "-i", str(tmp), "-o", str(png), "-b", "white", "-w", "900"],
                    check=True, timeout=180,
                )
                tmp.unlink(missing_ok=True)
                if not png.exists():
                    raise FileNotFoundError("渲染命令未产出 PNG")
                rel = png.relative_to(base_dir).as_posix()
                body = body[:m.start()] + f"![图：Mermaid 示意图]({rel})" + body[m.end():]
                continue
            except Exception as e:
                warnings.append(f"第 {i} 个 Mermaid 块渲染失败（{mermaid_cmd}）：{e}")
        # 未渲染：占位 + 警告
        unrendered += 1
        esc = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        placeholder = (
            '<div style="border:1px dashed #999;border-radius:6px;padding:14px;margin:20px 0;'
            'background:#fafafa;color:#666;font-size:13px;line-height:1.7;">'
            '<b>Mermaid 图未渲染</b>（微信公众号不支持 Mermaid，请安装 mermaid-cli 后重新生成）<br>'
            f'<pre style="white-space:pre-wrap;margin:8px 0 0;">{esc}</pre></div>'
        )
        body = body[:m.start()] + placeholder + body[m.end():]
        warnings.append(f"第 {i} 个 Mermaid 块未渲染，已保留源码占位")
    if for_publish and unrendered:
        raise RuntimeError(f"{unrendered} 个 Mermaid 块未渲染，发布中止。请安装 mermaid-cli（mmdc）并配置 publish.mermaid_cmd。")
    return body, unrendered, warnings


# ============================================================
# Markdown → HTML 转换
# ============================================================

def _apply_inline_style(soup, tag, style):
    for el in soup.find_all(tag):
        old = el.get("style", "")
        el["style"] = (old + ";" + style).strip(";") if old else style


def _format_num(n, fmt):
    if fmt == "roman_lower":
        return _to_roman(n).lower()
    if fmt == "roman_upper":
        return _to_roman(n).upper()
    if fmt == "padded":
        return f"{n:02d}"
    return str(n)


def _to_roman(n):
    table = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
             (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
             (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in table:
        while n >= v:
            out += s
            n -= v
    return out


def convert_fallback(text, theme_json):
    """md → 微信 HTML：python-markdown 解析 + BeautifulSoup 套主题内联样式。"""
    try:
        import markdown as md
        from bs4 import BeautifulSoup
    except ImportError as e:
        raise RuntimeError(f"缺少依赖 {e.name}，请先安装：pip install markdown beautifulsoup4") from e

    styles = theme_json.get("styles", {})
    highlights = theme_json.get("highlights", {})

    # —— 行内高亮标记（==、++、%%、&&、!!、@@、^^）注册为库扩展 ——
    from markdown.extensions import Extension
    from markdown.inlinepatterns import InlineProcessor
    import xml.etree.ElementTree as etree

    class _HighlightInline(InlineProcessor):
        def __init__(self, pattern, style, md_inst=None):
            super().__init__(pattern, md_inst)
            self.style = style

        def handleMatch(self, m, data):
            el = etree.Element("span")
            el.set("style", self.style)
            el.text = m.group(1)
            return el, m.start(), m.end()

    class HighlightExtension(Extension):
        MARKERS = [
            (r"==([^\n]+?)==", "hl_yellow"),
            (r"\+\+([^\n]+?)\+\+", "hl_blue"),
            (r"%%([^\n]+?)%%", "hl_pink"),
            (r"&&([^\n]+?)&&", "hl_green"),
            (r"!!([^\n]+?)!!", "em_red"),
            (r"@@([^\n]+?)@@", "em_blue"),
            (r"\^\^([^\n]+?)\^\^", "em_orange"),
        ]

        def __init__(self, highlights_dict, **kwargs):
            super().__init__(**kwargs)
            self.highlights = highlights_dict or {}

        def extendMarkdown(self, mdp):
            for pattern, key in self.MARKERS:
                style = self.highlights.get(key, "")
                if style:
                    mdp.inlinePatterns.register(
                        _HighlightInline(pattern, style, mdp), f"ftz-{key}", 180
                    )

    raw = md.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", HighlightExtension(highlights)]
    ).convert(text)
    soup = BeautifulSoup(raw, "html.parser")
    mapping = {
        "h1": styles.get("h1"), "h2": styles.get("h2"), "h3": styles.get("h3"),
        "p": styles.get("p"), "blockquote": styles.get("blockquote"), "img": styles.get("img"),
        "strong": styles.get("strong"), "em": styles.get("em"),
        "ul": styles.get("ul"), "ol": styles.get("ol"), "li": styles.get("li"),
        "hr": styles.get("hr"), "a": styles.get("a"),
        "table": styles.get("table"), "th": styles.get("th"), "td": styles.get("td"),
    }
    for tag, style in mapping.items():
        if style:
            _apply_inline_style(soup, tag, style)
    for code in soup.find_all("code"):
        style = styles.get("code_inline", "")
        if style and not code.find_parent("pre"):
            code["style"] = style
    for pre in soup.find_all("pre"):
        style = styles.get("code_block", "")
        if style:
            pre["style"] = style
        # 微信不认 white-space: pre，会把换行折叠；这里统一追加
        # white-space: pre-wrap（浏览器长行折行）+ word-break，保证微信端可读。
        base_style = pre.get("style", "").rstrip("; ")
        pre["style"] = f"{base_style}; white-space: pre-wrap; word-break: break-word"
        code = pre.find("code")
        if code is not None:
            text = code.get_text()
            code.clear()
            for i, line in enumerate(text.split("\n")):
                if i:
                    code.append(soup.new_tag("br"))
                line = line.rstrip("\r")
                indent = len(line) - len(line.lstrip(" "))
                if indent:
                    # 用真正的 NBSP 字符，BeautifulSoup 序列化时输出为 &nbsp; 实体；
                    # 直接 append 字面 "&nbsp;" 会被当作文本并双重转义成 "&amp;nbsp;"。
                    code.append("\u00a0" * indent)
                    line = line[indent:]
                code.append(line)
    # 列表序号 / 项目符号（主题 list_style）
    list_style = theme_json.get("list_style", {}) or {}
    num_container = list_style.get("num_container", "")
    num_prefix = list_style.get("num_prefix", "")
    num_suffix = list_style.get("num_suffix", ".")
    num_fmt = list_style.get("num_formatter", "decimal")
    bullet_container = list_style.get("bullet_container", "")
    bullet_char = list_style.get("bullet_char", "•")
    for ol in soup.find_all("ol"):
        for i, li in enumerate(ol.find_all("li", recursive=False), 1):
            span = soup.new_tag("span", style=num_container)
            span.string = f"{num_prefix}{_format_num(i, num_fmt)}{num_suffix}"
            li.insert(0, span)
    for ul in soup.find_all("ul"):
        for li in ul.find_all("li", recursive=False):
            span = soup.new_tag("span", style=bullet_container)
            span.string = bullet_char
            li.insert(0, span)
    # 分隔线 → 主题分节符
    divider_text = theme_json.get("section_divider_text") or "● ● ●"
    divider_style = styles.get("section_divider", "")
    for hr in soup.find_all("hr"):
        d = soup.new_tag("div", style=divider_style)
        d.string = divider_text
        hr.replace_with(d)
    # NBSP 统一输出为 &nbsp; 实体（微信编辑器兼容性最好），
    # 避免 BeautifulSoup 直接序列化出原始 U+00A0 字符。
    return str(soup).replace("\u00a0", "&nbsp;")


# ============================================================
# 主流程
# ============================================================

def convert_article(md_path, out_path=None, theme_arg=None, html_dir="html",
                    mermaid_cmd=None, for_publish=False, dry_run=False):
    """把一篇 md 转成 HTML。返回 (out_path, meta dict)。"""
    md_path = Path(md_path)
    if not md_path.exists():
        raise FileNotFoundError(f"文章不存在：{md_path}")

    theme_slug = pick_theme(theme_arg)
    theme_json = load_theme_json(theme_slug)

    md_text = md_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(md_text)
    title = extract_title(fm, body)
    digest = extract_digest(fm, body)
    cover = fm.get("cover") or ""

    if out_path is None:
        out_path = md_path.parent / html_dir / f"{md_path.stem}.html"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        return out_path, {
            "theme": theme_slug, "title": title, "digest": digest,
            "cover": cover, "mermaid_blocks": 0, "warnings": [],
            "dry_run": True,
        }

    body, unrendered, warnings = render_mermaid_blocks(
        body, md_path.parent, out_path, mermaid_cmd, for_publish
    )

    content_html = convert_fallback(body, theme_json)

    body_style = theme_json.get("styles", {}).get("body", "")
    full_html = (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n"
        "<meta charset=\"UTF-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        f"<title>{title}</title>\n</head>\n"
        f"<body style=\"{body_style}\">\n{content_html}\n</body>\n</html>\n"
    )
    out_path.write_text(full_html, encoding="utf-8")
    try:
        update_frontmatter(md_path, status_add="已生成html")
    except Exception as e:  # 状态回写失败不影响 HTML 产出
        warnings.append(f"frontmatter 状态回写失败：{e}")

    meta = {
        "theme": theme_slug, "title": title, "digest": digest, "cover": cover,
        "mermaid_blocks": unrendered, "warnings": warnings, "dry_run": False,
    }
    return out_path, meta


def main():
    parser = argparse.ArgumentParser(description="md → 微信兼容 HTML（from-zero-tutorial）")
    parser.add_argument("--input", "-i", required=True, help="文章 Markdown 路径")
    parser.add_argument("--out", "-o", help="输出 HTML 路径（默认 <文章目录>/html/<文章名>.html）")
    parser.add_argument("--html-dir", default="html", help="HTML 输出目录（相对文章目录，默认 html）")
    parser.add_argument("--theme", help="主题 slug（themes/*.json）；缺省随机")
    parser.add_argument("--mermaid-cmd", default="mmdc", help="mermaid 渲染命令（默认 mmdc，找不到则保留源码占位）")
    parser.add_argument("--for-publish", action="store_true", help="发布模式：mermaid 未渲染则中止")
    parser.add_argument("--dry-run", action="store_true", help="只打印将用的主题/输出，不写文件")
    args = parser.parse_args()

    out, meta = convert_article(
        args.input, args.out, args.theme, html_dir=args.html_dir,
        mermaid_cmd=args.mermaid_cmd,
        for_publish=args.for_publish, dry_run=args.dry_run,
    )
    print(f"[主题] {meta['theme']}")
    print(f"[标题] {meta['title']}")
    print(f"[摘要] {meta['digest'][:50]}")
    print(f"[封面] {meta.get('cover') or '（未设置，发布时可用 --cover 指定）'}")
    if meta["dry_run"]:
        print(f"[输出]（干跑）{out}")
        return
    for w in meta["warnings"]:
        print(f"[警告] {w}")
    print(f"[输出] {out}（{out.stat().st_size} 字节）")


if __name__ == "__main__":
    main()
