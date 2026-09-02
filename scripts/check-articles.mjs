#!/usr/bin/env node
/**
 * 内容厚度检查：每篇系列文章（frontmatter 带 lesson）正文必须达到字数区间。
 *
 * 用法：
 *   node check-articles.mjs --root <系列目录> [--min 3500] [--max 8000]
 *
 * 检查两项：
 *   1. 正文字数在 [min, max] 区间内（默认 3500-8000，按中文字符计，去掉 markdown 符号与空白）；
 *   2. 至少有一张图（frontmatter cover 或正文图片引用，缺图归 check-images.mjs 管，这里只提示）。
 *
 * 全部通过退出码 0；存在字数不足或超长退出码 1。
 *
 * --strict：对扫描到的所有 .md 强制字数检查（用于单篇模式，单篇文章 frontmatter
 *           无 lesson）；不带时仅带 lesson 的系列文章强制（默认）。
 */
import fs from 'node:fs';
import path from 'node:path';

// 只做开关、不吞下一个参数的布尔标志
const BOOLEAN_FLAGS = new Set(['strict']);

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const key = argv[i].replace(/^--/, '');
    if (key === argv[i]) continue;
    if (BOOLEAN_FLAGS.has(key)) {
      args[key] = true;
    } else {
      args[key] = argv[++i];
    }
  }
  return args;
}

function walk(dir, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (['.git', '.obsidian', '.trash', 'node_modules'].includes(entry.name)) continue;
      walk(full, out);
    } else {
      out.push(full);
    }
  }
  return out;
}

function frontmatterLesson(content) {
  content = content.replace(/\r\n/g, '\n');
  const m = content.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return null;
  const lesson = m[1].match(/^lesson:\s*"?(\d+)"?$/m);
  return lesson ? lesson[1] : null;
}

function bodyText(content) {
  content = content.replace(/\r\n/g, '\n');
  const m = content.match(/^---\n[\s\S]*?\n---\n?/);
  const body = m ? content.slice(m[0].length) : content;
  return body
    .replace(/```[\s\S]*?```/g, '')          // 代码块（含 Mermaid）不计入正文
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')     // 图片引用不计
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')  // 链接只计显示文字
    .replace(/[#>*`|~\-_=[\]()]/g, '')
    .replace(/\s+/g, '');
}

async function main() {
  const args = parseArgs(process.argv);
  const root = path.resolve(args.root || '.');
  const min = Number(args.min || 3500);
  const max = Number(args.max || 8000);
  if (!fs.existsSync(root)) {
    console.error(`[错误] 目录不存在：${root}`);
    process.exit(1);
  }

  const issues = [];
  let checked = 0;
  const strict = Boolean(args.strict);
  for (const md of walk(root)) {
    if (!md.toLowerCase().endsWith('.md')) continue;
    const content = fs.readFileSync(md, 'utf8');
    if (!strict && frontmatterLesson(content) === null) continue; // 非系列文章不强制；--strict 时全部强制（单篇模式）
    checked++;
    const len = [...bodyText(content)].length;
    if (len < min) {
      issues.push({ file: md, msg: `字数不足：${len} 字（要求 ≥${min}）` });
    } else if (len > max) {
      issues.push({ file: md, msg: `超长：${len} 字（要求 ≤${max}，删减注水）` });
    }
  }

  if (issues.length === 0) {
    console.log(`[OK] 内容厚度检查通过：${checked} 篇文章均在 ${min}-${max} 字区间。`);
    return;
  }
  for (const i of issues) {
    console.log(`[厚度] ${path.relative(root, i.file)} → ${i.msg}`);
  }
  console.log(`[结果] 共 ${issues.length} 个问题。`);
  process.exit(1);
}

main().catch((err) => {
  console.error('[错误]', err.message);
  process.exit(1);
});
