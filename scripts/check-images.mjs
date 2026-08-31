#!/usr/bin/env node
/**
 * 配图一一对应核对脚本（check-images）
 *
 * 在系列目录下运行：
 *   node <skill 路径>/scripts/check-images.mjs --root "<系列目录>"
 *
 * 检查四项：
 *   1. 正向：正文每个图片引用都能找到对应文件（断链检查）
 *   2. 反向：assets/ 下每个图片文件至少被引用一次（未用图检查）
 *   3. 缺封面：每篇带 lesson 的系列文章必须配置 frontmatter cover
 *   4. 缺正文图：每篇带 lesson 的文章正文（frontmatter 之外）必须至少引用一张非封面的图
 *
 * 支持三种引用形式：
 *   - Markdown 图片语法：![说明](assets/NN/05-01.png)
 *   - Obsidian 嵌入：![[05-01.png]]（按文件名在 assets/ 下匹配）
 *   - frontmatter 封面登记：cover: assets/cover-NN.png
 *
 * 全部通过退出码 0；存在断链、未用图或缺图退出码 1。
 */
import fs from 'node:fs';
import path from 'node:path';

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const key = argv[i].replace(/^--/, '');
    if (key === argv[i]) continue;
    args[key] = argv[++i];
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

const IMG_RE = /!\[[^\]]*\]\(([^)]+)\)/g;
const WIKI_IMG_RE = /!\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]/g;
const IMG_EXT = /\.(png|jpe?g|gif|webp|svg|bmp|avif)$/i;

function normalize(p) {
  return path.resolve(p).toLowerCase();
}

function frontmatterCover(content) {
  content = content.replace(/\r\n/g, '\n');
  const m = content.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return null;
  const cover = m[1].match(/^cover:\s*["']?([^\s"']+)["']?$/m);
  return cover ? cover[1] : null;
}

function frontmatterLesson(content) {
  content = content.replace(/\r\n/g, '\n');
  const m = content.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return null;
  const lesson = m[1].match(/^lesson:\s*"?(\d+)"?$/m);
  return lesson ? lesson[1] : null;
}

function bodyImageRefs(content, coverBase) {
  content = content.replace(/\r\n/g, '\n');
  const m = content.match(/^---\n[\s\S]*?\n---\n?/);
  const body = m ? content.slice(m[0].length) : content;
  const refs = [];
  let r;
  IMG_RE.lastIndex = 0;
  while ((r = IMG_RE.exec(body)) !== null) {
    const raw = r[1].trim();
    if (!raw || raw.startsWith('http://') || raw.startsWith('https://') || raw.startsWith('data:')) continue;
    const clean = raw.split(/\s+/)[0].replace(/["']$/, '');
    if (coverBase && path.basename(clean).toLowerCase() === coverBase) continue; // 封面引用不算正文配图
    refs.push(clean);
  }
  WIKI_IMG_RE.lastIndex = 0;
  while ((r = WIKI_IMG_RE.exec(body)) !== null) {
    const raw = r[1].trim();
    if (!IMG_EXT.test(raw)) continue;
    if (coverBase && raw.toLowerCase() === coverBase) continue;
    refs.push(raw);
  }
  return refs;
}

async function main() {
  const args = parseArgs(process.argv);
  const root = path.resolve(args.root || '.');
  if (!fs.existsSync(root)) {
    console.error(`[错误] 目录不存在：${root}`);
    process.exit(1);
  }

  const allFiles = walk(root);
  const mdFiles = allFiles.filter((f) => f.toLowerCase().endsWith('.md'));
  const missingCover = [];
  const missingBodyImage = [];
  for (const md of mdFiles) {
    const content = fs.readFileSync(md, 'utf8').replace(/\r\n/g, '\n');
    if (frontmatterLesson(content) === null) continue; // 非系列文章（规划/素材库等）不强制配图
    const cover = frontmatterCover(content);
    if (!cover) {
      missingCover.push(md);
      continue;
    }
    if (bodyImageRefs(content, path.basename(cover).toLowerCase()).length === 0) {
      missingBodyImage.push(md);
    }
  }
  const imageFiles = allFiles.filter((f) => IMG_EXT.test(f));
  const imageSet = new Set(imageFiles.map((f) => normalize(f)));
  const baseNameIndex = new Map();
  for (const f of imageFiles) {
    baseNameIndex.set(path.basename(f).toLowerCase(), f);
  }

  const refs = [];
  for (const md of mdFiles) {
    const content = fs.readFileSync(md, 'utf8').replace(/\r\n/g, '\n');
    const dir = path.dirname(md);
    const cover = frontmatterCover(content);
    if (cover) refs.push({ file: md, target: path.resolve(dir, cover) });

    let m;
    IMG_RE.lastIndex = 0;
    while ((m = IMG_RE.exec(content)) !== null) {
      const raw = m[1].trim();
      if (!raw || raw.startsWith('http://') || raw.startsWith('https://') || raw.startsWith('data:')) continue;
      const clean = raw.split(/\s+/)[0].replace(/["']$/, '');
      refs.push({ file: md, target: path.resolve(dir, clean) });
    }

    WIKI_IMG_RE.lastIndex = 0;
    while ((m = WIKI_IMG_RE.exec(content)) !== null) {
      const raw = m[1].trim();
      if (!IMG_EXT.test(raw)) continue;
      refs.push({ file: md, target: raw, wiki: true });
    }
  }

  const broken = [];
  for (const r of refs) {
    if (r.wiki) {
      if (!baseNameIndex.has(r.target.toLowerCase())) {
        broken.push({ ...r, reason: `嵌入 ![[${r.target}]] 未找到同名图片` });
      }
    } else if (!imageSet.has(normalize(r.target))) {
      broken.push({ ...r, reason: `引用文件不存在：${r.target}` });
    }
  }

  const usedKeys = new Set();
  for (const r of refs) {
    if (r.wiki) {
      const found = baseNameIndex.get(r.target.toLowerCase());
      if (found) usedKeys.add(normalize(found));
    } else {
      usedKeys.add(normalize(r.target));
    }
  }
  const unused = imageFiles.filter((f) => !usedKeys.has(normalize(f)));

  const problems = broken.length + unused.length + missingCover.length + missingBodyImage.length;
  if (problems === 0) {
    console.log(`[OK] 配图检查通过：${refs.length} 处引用，${imageFiles.length} 个图片文件，无断链、无未用图、无缺封面、无缺正文图。`);
    return;
  }
  for (const b of broken) {
    console.log(`[断链] ${path.relative(root, b.file)} → ${b.reason}`);
  }
  for (const u of unused) {
    console.log(`[未用] ${path.relative(root, u)}`);
  }
  for (const mc of missingCover) {
    console.log(`[缺封面] ${path.relative(root, mc)}`);
  }
  for (const mb of missingBodyImage) {
    console.log(`[缺正文图] ${path.relative(root, mb)}`);
  }
  console.log(`[结果] 共 ${problems} 个问题（断链 ${broken.length}、未用图 ${unused.length}、缺封面 ${missingCover.length}、缺正文图 ${missingBodyImage.length}）。`);
  process.exit(1);
}

main().catch((err) => {
  console.error('[错误]', err.message);
  process.exit(1);
});
