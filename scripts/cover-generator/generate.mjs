#!/usr/bin/env node
/**
 * 模板化配图生成器：HTML/CSS 模板 + 无头浏览器截图。
 *
 * 用法示例：
 *   node generate.mjs --series "高中数学竞赛零基础入门" --lesson 00 --title "这个系列怎么学"
 *     --subtitle "一条不赌天赋的路线图" --category "开篇" --out "assets/cover-00.png"
 *
 * 通用 HTML→PNG 引擎：封面与文章配图（知识卡、示意卡等）共用。
 *
 * 模板选择（优先级从高到低）：
 *   --template <path>  直接指定任意 HTML 模板文件（用于文章配图等非封面场景）
 *   --style <slug>     从 templates/manifest.json 按风格取模板；指定后一律按指定。
 *   --random           未指定 --style 时，从 33 套风格里随机选一套（默认行为，可省略）。
 *   --auto             可选：未指定 --style 时，按 --title/--subtitle/--category 关键词自动路由。
 *   注意：同一篇文章的封面与正文图应使用同一 --style，保证风格一致（正文卡通过
 *   {{PALETTE_BG/INK/SUB/ACCENT}} 占位符自动继承该风格配色）。
 *
 * 占位符：
 *   内置：{{SERIES}} {{LESSON}} {{TITLE}} {{TITLE_SIZE}} {{SUBTITLE}} {{CATEGORY}} {{TAG}} {{FOOTER}} {{FOOT}} {{DATE}}
 *   扩展：--set key=value（可重复），会把模板里的 {{key}} 替换为 value。
 *
 * 渲染通道（自动选择，无需手动配置）：
 *   1. 已安装 Playwright（npm i -D playwright + npx playwright install chromium）→ 用 Playwright；
 *   2. 否则找本机 Edge / Chrome / Chromium → 用 headless 截图（零依赖，Windows 自带 Edge 即可）；
 *   3. 都没有 → 报错并给出安装提示。
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

let MANIFEST;
try {
  MANIFEST = JSON.parse(
    fs.readFileSync(path.join(__dirname, 'templates', 'manifest.json'), 'utf8')
  );
} catch {
  console.error('[错误] 找不到 templates/manifest.json，请确认模板目录完整。');
  process.exit(1);
}

const BROWSER_CANDIDATES = [
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
];

const AUTO_ROUTE = [
  { slug: 'blueprint', keys: ['工程', '技术', '科学', '代码', '开发', '架构', '机器人', '物理', '化学', '数学'] },
  { slug: 'terminal', keys: ['终端', '命令行', '开发者', '极客', '编程', 'cli', '程序员'] },
  { slug: 'swiss', keys: ['数据', '报告', '政策', '升学', '奖项', '分析', '调研', '专业'] },
  { slug: 'editorial', keys: ['观点', '专栏', '长文', '深度', '评论', '杂志'] },
  { slug: 'ink', keys: ['文化', '国学', '传统', '书法', '诗词', '历史', '水墨'] },
  { slug: 'guochao', keys: ['国潮', '节庆', '春节', '中秋', '年味', '中式'] },
  { slug: 'sketch', keys: ['教程', '科普', '讲解', '入门', '手绘', '笔记', '学习'] },
  { slug: 'aurora', keys: ['ai', '人工智能', '科技', '未来', '氛围'] },
  { slug: 'pixel', keys: ['游戏', '复古', '像素', '8bit'] },
  { slug: 'vapor', keys: ['音乐', '播客', '蒸汽', '电子'] },
  { slug: 'memphis', keys: ['潮流', '年轻', '娱乐', '活动', '市集'] },
];

function autoRoute(args) {
  const text = [args.title, args.subtitle, args.category].filter(Boolean).join(' ').toLowerCase();
  for (const r of AUTO_ROUTE) {
    if (r.keys.some((k) => text.includes(k.toLowerCase()))) return r.slug;
  }
  return 'default';
}

function randomStyle() {
  const keys = Object.keys(MANIFEST);
  return keys[Math.floor(Math.random() * keys.length)];
}

function parseArgs(argv) {
  const args = {};
  const sets = [];
  for (let i = 2; i < argv.length; i++) {
    const key = argv[i].replace(/^--/, '');
    if (key === argv[i]) continue;
    if (key === 'set') {
      const kv = argv[++i];
      const idx = kv.indexOf('=');
      if (idx > 0) sets.push([kv.slice(0, idx), kv.slice(idx + 1)]);
    } else {
      args[key] = argv[++i];
    }
  }
  args._sets = sets;
  return args;
}

function titleSize(title) {
  const len = [...title].length;
  if (len <= 10) return 64;
  if (len <= 18) return 48;
  return 38;
}

function findBrowser() {
  for (const candidate of BROWSER_CANDIDATES) {
    try {
      if (fs.existsSync(candidate)) return candidate;
    } catch {
      /* 忽略 */
    }
  }
  return null;
}

function renderTemplate(options) {
  let template;
  if (options.template) {
    const p = path.resolve(options.template);
    if (!fs.existsSync(p)) throw new Error(`找不到模板文件：${p}`);
    template = fs.readFileSync(p, 'utf8');
  } else {
    const style = options.style || 'default';
    const entry = MANIFEST[style];
    if (!entry) {
      const available = Object.keys(MANIFEST).join(', ');
      throw new Error(`未知风格：${style}。可用风格：${available}`);
    }
    template = fs.readFileSync(path.join(__dirname, 'templates', entry.file), 'utf8');
  }
  const setKeys = new Set((options._sets || []).map(([k]) => k));
  const builtins = {
    WIDTH: options.width,
    HEIGHT: options.height,
    SERIES: options.series,
    LESSON: options.lesson,
    TITLE: options.title,
    TITLE_SIZE: titleSize(options.title),
    SUBTITLE: options.subtitle,
    CATEGORY: options.category,
    TAG: options.tag,
    FOOTER: options.footer,
    FOOT: options.footer,
    DATE: options.date,
  };
  let html = template;
  // 用解析后的 style（--style 指定 / --auto 路由 / 随机结果），保证 PALETTE_* 与模板风格一致
  const palette = MANIFEST[options.style]?.palette || { bg: '#0f172a', ink: '#f8fafc', sub: '#94a3b8', accent: '#f59e0b' };
  const paletteKeys = {
    PALETTE_BG: palette.bg,
    PALETTE_INK: palette.ink,
    PALETTE_SUB: palette.sub,
    PALETTE_ACCENT: palette.accent,
  };
  for (const [k, v] of Object.entries(paletteKeys)) {
    if (setKeys.has(k)) continue;
    html = html.replaceAll(`{{${k}}}`, v);
  }
  for (const [k, v] of Object.entries(builtins)) {
    if (setKeys.has(k)) continue; // --set 提供的键优先，内置不覆盖
    html = html.replaceAll(`{{${k}}}`, v);
  }
  for (const [k, v] of options._sets || []) {
    html = html.replaceAll(`{{${k}}}`, v);
  }
  const leftovers = [...html.matchAll(/\{\{([A-Za-z0-9_]+)\}\}/g)].map((m) => m[1]);
  if (leftovers.length) {
    console.warn(`[警告] 以下占位符未替换，出图会残留：${[...new Set(leftovers)].join(', ')}`);
  }
  return html;
}

function screenshotWithPlaywright(htmlPath, args, out) {
  return import('playwright').then(async (playwright) => {
    const browser = await playwright.chromium.launch();
    try {
      const page = await browser.newPage({
        viewport: { width: args.width, height: args.height },
        deviceScaleFactor: args.scale,
      });
      await page.goto(`file:///${htmlPath.replaceAll('\\', '/')}`, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({ path: out, type: 'png' });
    } finally {
      await browser.close();
    }
  });
}

function screenshotWithBrowser(browser, htmlPath, args, out) {
  const url = 'file:///' + encodeURI(htmlPath.replaceAll('\\', '/'));
  const browserArgs = [
    '--headless',
    '--disable-gpu',
    '--no-first-run',
    '--disable-extensions',
    '--hide-scrollbars',
    `--force-device-scale-factor=${args.scale}`,
    `--window-size=${args.width},${args.height}`,
    '--virtual-time-budget=2000',
    `--screenshot=${out}`,
    url,
  ];
  execFileSync(browser, browserArgs, { stdio: 'ignore' });
}

function main() {
  const args = parseArgs(process.argv);
  const localDate = () => {
    const d = new Date();
    const p = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
  };
  const options = {
    style: args.style || (args.auto ? autoRoute(args) : randomStyle()),
    template: args.template || null,
    series: args.series || '',
    lesson: String(args.lesson ?? '').padStart(2, '0'),
    title: args.title || '未命名标题',
    subtitle: args.subtitle || '',
    category: args.category || '',
    tag: args.tag || '',
    footer: args.footer || (args.series ? `${args.series} · 系列教程` : ''),
    date: args.date || localDate(),
    width: Number(args.width || 1200),
    height: Number(args.height || 630),
    scale: Number(args.scale || 2),
    _sets: args._sets || [],
  };
  const out = path.resolve(args.out || 'cover.png');
  // 统一先建输出目录：Playwright 截图不会自动创建父目录，与浏览器 fallback 保持一致
  fs.mkdirSync(path.dirname(out), { recursive: true });
  if (args.auto && !args.style) {
    console.log(`[路由] 未指定 --style，关键词自动路由 → ${options.style}`);
  } else if (!args.style) {
    console.log(`[路由] 未指定 --style，随机匹配 → ${options.style}`);
  }

  const html = renderTemplate(options);
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cover-'));
  const htmlPath = path.join(tmpDir, 'cover.html');
  fs.writeFileSync(htmlPath, html, 'utf8');

  const run = async () => {
    try {
      try {
        await screenshotWithPlaywright(htmlPath, options, out);
      console.log(`[OK] 已用 Playwright 生成封面（风格：${options.style}）：${out}`);
        return;
      } catch (err) {
        if (err && err.code === 'ERR_MODULE_NOT_FOUND') {
          // 未安装 Playwright，走浏览器通道
        } else {
          throw err;
        }
      }

      const browser = findBrowser();
      if (!browser) {
        throw new Error(
          '未安装 Playwright 也找不到本机 Edge/Chrome。请先执行：npm i -D playwright 和 npx playwright install chromium，或安装 Edge。'
        );
      }
      screenshotWithBrowser(browser, htmlPath, options, out);
      if (!fs.existsSync(out)) {
        throw new Error('浏览器截图未产出文件：' + out);
      }
      console.log(`[OK] 已用本机 ${path.basename(browser)} 生成封面（风格：${options.style}）：${out}`);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  };

  run().catch((err) => {
    console.error('[错误]', err.message);
    process.exit(1);
  });
}

main();
