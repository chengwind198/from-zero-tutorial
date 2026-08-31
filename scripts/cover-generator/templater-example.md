# Obsidian / Templater 集成示例

把下面的 `obsidian-cover.js` 保存到 Templater 设置里指定的 Scripts folder（例如 vault 的 `90 - tools/templater-scripts`），然后在笔记模板中调用：

```text
<% tp.user.obsidian_cover(tp) %>
```

脚本会读取当前笔记 frontmatter 的 `title / subtitle / lesson / category / series / style`，调用 [generate.mjs](generate.mjs) 生成 `assets/cover-NN.png`，并把 `cover` 字段写回 frontmatter，最后返回一个可插入正文的图片引用。`style` 可选，填模板风格 slug（见 templates/manifest.json）；不填默认随机选一套。

```js
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

async function obsidian_cover(tp) {
  const fm = tp.frontmatter || {};
  const title = (fm.title || tp.file.title).replace(/[\\/:*?"<>|]/g, '-');
  const subtitle = fm.subtitle || '';
  const lesson = String(fm.lesson ?? '00').padStart(2, '0');
  const category = Array.isArray(fm.category) ? fm.category[0] : (fm.category || '');
  const series = fm.series || '';
  const styleArgs = fm.style ? ['--style', fm.style] : ['--random'];

  // 把 <SKILL_ROOT> 换成你机器上 from-zero-tutorial 技能目录的实际路径
  // （跨机器通用写法：先 cd 到技能目录，或复制 generate.mjs 到 vault 内再用 vault 相对路径）
  const script = '<SKILL_ROOT>/scripts/cover-generator/generate.mjs';
  const outDir = path.join(tp.file.folder(true), 'assets');
  fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, `cover-${lesson}.png`);

  execFileSync('node', [
    script,
    ...styleArgs,
    '--series', series,
    '--lesson', lesson,
    '--title', title,
    '--subtitle', subtitle,
    '--category', category,
    '--out', outFile,
  ]);

  const file = tp.app.vault.getAbstractFileByPath(tp.file.path);
  await tp.app.fileManager.processFrontMatter(file, (fmData) => {
    fmData.cover = `assets/cover-${lesson}.png`;
  });

  return `![封面：${title}](assets/cover-${lesson}.png)`;
}

module.exports = obsidian_cover;
```

## 注意事项

- Templater user script 运行在 Node 环境；若沙箱拦截 `require`，在 Templater 设置里关闭 JavaScript sandboxing；
- 首次使用前装依赖：在 skill 的 `scripts/cover-generator` 目录执行 `npm i -D playwright` 和 `npx playwright install chromium`；
- 更稳的做法是把 `generate.mjs` 与 `cover.html` 复制到 vault 内（如 `90 - tools/cover-generator/`），再改脚本里的路径；
- 批量补图：对已经写完的系列文章，循环补生成 `cover-NN.png`；每篇按 frontmatter `style` 传同一 slug（未指定则各自随机），保证同篇一致即可，不必全系列统一。
