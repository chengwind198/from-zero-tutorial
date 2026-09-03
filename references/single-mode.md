# 单篇模式流程（Single Article Mode）

> 由 SKILL.md「模式路由」命中单篇模式后使用。**只按本文件执行**，禁止执行系列专属节点：
> 不建系列规划.md、不建素材库.md、frontmatter 不写 lesson、正文不写「下一步」、收尾不回填三处。

## 适用场景

用户只给一个标题或主题，要求写一篇文章（公众号文章、独立文章）；或路由无法判断默认落入单篇模式。

## 五步流程

### 1. 取材（铁律）

web search 只针对本文主题；关键数据双源核实（至少两个独立来源），来源与核验日期记入「本文素材清单」（对话内或文末参考节）；禁止编造案例、数据、对话。材料不齐不写。

### 2. 大纲

动笔前在对话中给出简短大纲（3-5 个正文小节 + 配图规划），不落盘文件。

### 3. 写作

- 正文字数 3500–8000（check-articles.mjs 默认区间，与系列一致）；
- 规范同 references/article.md：场景开场、术语首现一句话解释、至少 1 个真实案例、至少 1 组数据表、误区澄清、延伸阅读、一稿二改去 AI 味；
- 标题：用户给定标题（含主题关键词利于搜索）；
- frontmatter：用 assets/templates/article-single-template.md（无 lesson）；
- 章节结构：正文 →（操作类加「本节难点/要点速记/动手任务/完成标志/Q&A」）→ 参考；不设「下一步」，也不在正文里写「配图登记」（图片锚点登记写进对话/交付说明即可）。

### 4. 配图（强制）

- 封面：`node scripts/cover-generator/generate.mjs --input "<文章.md>" --width 1068 --height 455 --out "assets/<文件名>.png"`（公众号 2.35:1；title 自动取 frontmatter title）；把随机到的 style slug 回填 frontmatter `style`；
- 正文图：正文每个一级小节（## 标题）至少 1 张（同一张图不跨小节复用），与封面同一 style（figures 模板或真实截图）；「本节难点 / 要点速记 / 动手任务 / 完成标志 / 常见问题 Q&A / 参考 / 下一步 / 延伸阅读 / 配图登记」等辅助或收尾小节不计入；
- 目录：封面与正文图都放文章目录 `assets/` 下即可（不强制 assets/NN/）。

### 5. 验证与收尾

1. `node scripts/check-images.mjs --root "<文章目录>" --strict` —— 必须 0 断链、0 未用图、0 缺封面、0 缺正文图、0 缺小节图；
2. `node scripts/check-articles.mjs --root "<文章目录>" --strict` —— 字数 3500–8000；
3. `python scripts/md-to-html.py --input "<文章.md>"` —— 微信兼容 HTML，无 `{{...}}` 残留；
4. `python scripts/publish-wechat.py --input "<文章.md>" --dry-run` —— 核对账号/标题/图片清单；正式发布必须先得到用户确认；
5. 图片锚点回填：文章位于已有系列目录内 → 并入该系列素材库.md 对应条目（封面/正文图文件名 + 锚点说明，写法同系列 17–20 课）；完全独立的单篇 → 图片锚点登记只写进对话/交付说明，不写入文章正文；
6. 收尾产物只应有：文章 .md、assets/ 图片、（可选）html/、（若发布）发布记录。

## 与系列模式差异速查

| 差异点 | 系列模式 | 单篇模式 |
| --- | --- | --- |
| frontmatter lesson | 必填 | 无 |
| 「下一步」章节 | 必设 | 不设（以延伸阅读收尾） |
| 系列规划.md / 素材库.md | 必建 | 不建 |
| 回填 | 进度表 + 合集 + 素材库三处必做 | 仅图片锚点登记（系列目录内必做，独立单篇可选） |
| 配图校验 | check-images.mjs（默认） | check-images.mjs --strict |
| 字数校验 | check-articles.mjs（默认，仅带 lesson） | check-articles.mjs --strict |
| 升级为系列 | — | 补建规划.md + 素材库.md + lesson + 「下一步」后继续 |
