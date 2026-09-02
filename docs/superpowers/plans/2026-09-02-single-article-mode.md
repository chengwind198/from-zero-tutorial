# 单篇模式（single-article mode）实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 from-zero-tutorial 技能内新增"单篇模式"：入口按请求自动路由系列/单篇，单篇走轻量五步（不建规划/素材库、无 lesson/下一步、配图强制并用 check-images --strict），系列模式行为不变。

**Architecture:** 单 skill 双模式。SKILL.md 顶部加"模式路由 + 执行纪律"，原七步原位保留（系列模式）；单篇五步细节独立成 references/single-mode.md；写作规范 article.md 与系列模板加模式差异标注，新增单篇模板；check-images.mjs 加 --strict 参数让无 lesson 的单篇也强制封面/正文图。所有脚本/模板/主题共享一份，不复制。

**Tech Stack:** Node.js（check-images.mjs）、Python（md-to-html/publish）、Markdown 文档（SKILL.md/references/templates）、git。

**Spec:** docs/superpowers/specs/2026-09-02-single-article-mode-design.md（v3，commit 639e205）

---

## 当前工作区注意

- 仓库 C:\git\from-zero-tutorial 存在上一轮未提交改动（SKILL.md、references/images.md、scripts/cover-generator/generate.mjs、scripts/cover-generator/templater-example.md，即 generate.mjs 的 --input 功能），本计划在其之上继续，**不要覆盖/回退**这些改动。
- 沙箱故障期间命令需 require_escalated；文件编辑用临时 Python 脚本（apply_patch 不可用时）。
- 所有文档/代码中文（AGENTS.md）。

## File Structure

| 文件 | 责任 | 动作 |
| --- | --- | --- |
| scripts/check-images.mjs | 配图校验；新增 --strict | Modify |
| references/single-mode.md | 单篇五步全细节 | Create |
| SKILL.md | 路由 + 执行纪律 + description；七步原位为系列模式 | Modify |
| references/article.md | 共享写作规范；加模式差异标注 | Modify |
| assets/templates/article-single-template.md | 单篇 frontmatter/章节模板 | Create |
| assets/templates/article-template.md | 系列模板；加"单篇用单篇模板"指引 | Modify |

---

### Task 1: check-images.mjs 支持 --strict

**Files:**
- Modify: `scripts/check-images.mjs`
- Test: 临时目录行为验证（无测试框架，用命令断言）

- [ ] **Step 1: 修改头部用法注释**

在文件头部注释"全部通过退出码 0；存在断链、未用图或缺图退出码 1。"之后追加：

```
 *
 * --strict：对扫描到的所有 .md 强制缺封面/缺正文图检查（用于单篇模式，
 *           单篇文章 frontmatter 无 lesson）；不带时仅带 lesson 的系列文章强制（默认）。
```

- [ ] **Step 2: 修改强制检查条件**

定位 main() 中循环：

```js
  for (const md of mdFiles) {
    const content = fs.readFileSync(md, 'utf8').replace(/\r\n/g, '\n');
    if (frontmatterLesson(content) === null) continue; // 非系列文章（规划/素材库等）不强制配图
```

改为：

```js
  const strict = Boolean(args.strict);
  for (const md of mdFiles) {
    const content = fs.readFileSync(md, 'utf8').replace(/\r\n/g, '\n');
    if (!strict && frontmatterLesson(content) === null) continue; // 非系列文章不强制配图；--strict 时全部强制（单篇模式）
```

- [ ] **Step 3: 语法检查**

Run: `node --check scripts/check-images.mjs`
Expected: 无输出，退出码 0。

- [ ] **Step 4: 行为验证（三组样本，全部在临时目录）**

创建样本：

```powershell
$base = Join-Path $env:TEMP "fzt-strict-test"; Remove-Item -LiteralPath $base -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Join-Path $base "noLessonNoCover") | Out-Null
Set-Content -LiteralPath (Join-Path $base "noLessonNoCover\a.md") -Value "---`ntitle: 测试`n---`n正文" -Encoding UTF8
New-Item -ItemType Directory -Force -Path (Join-Path $base "lessonNoCover") | Out-Null
Set-Content -LiteralPath (Join-Path $base "lessonNoCover\b.md") -Value "---`ntitle: 测试`nlesson: 1`n---`n正文" -Encoding UTF8
```

Run: `node scripts/check-images.mjs --root <base>/noLessonNoCover`
Expected: `[OK] 配图检查通过`，退出码 0（无 lesson 且不带 --strict 不强制，改动前后一致）。

Run: `node scripts/check-images.mjs --root <base>/noLessonNoCover --strict`
Expected: 退出码 1，输出含 `[缺封面] a.md` 与 `[缺正文图] a.md`（新行为：--strict 强制无 lesson 文章）。

Run: `node scripts/check-images.mjs --root <base>/lessonNoCover`
Expected: 退出码 1，输出含 `[缺封面] b.md`（现有行为保留：带 lesson 仍强制）。

清理：`Remove-Item -LiteralPath <base> -Recurse -Force`

- [ ] **Step 5: Commit**

```bash
git add scripts/check-images.mjs
git commit -m "feat: check-images 支持 --strict 强制单篇配图校验"
```

### Task 2: 新增 references/single-mode.md

**Files:**
- Create: `references/single-mode.md`

- [ ] **Step 1: 写入完整文件**

将以下内容原样保存为 `references/single-mode.md`（UTF-8）：

```markdown
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
- 章节结构：正文 →（操作类加「本节难点/要点速记/动手任务/完成标志/Q&A」）→ 参考 →（可选「配图登记」）；不设「下一步」。

### 4. 配图（强制）

- 封面：`node scripts/cover-generator/generate.mjs --input "<文章.md>" --width 1068 --height 455 --out "assets/<文件名>.png"`（公众号 2.35:1；title 自动取 frontmatter title）；把随机到的 style slug 回填 frontmatter `style`；
- 正文图：至少 1 张，与封面同一 style（figures 模板或真实截图）；
- 目录：封面与正文图都放文章目录 `assets/` 下即可（不强制 assets/NN/）。

### 5. 验证与收尾

1. `node scripts/check-images.mjs --root "<文章目录>" --strict` —— 必须 0 断链、0 未用图、0 缺封面、0 缺正文图；
2. `node scripts/check-articles.mjs --root "<文章目录>"` —— 字数 3500–8000；
3. `python scripts/md-to-html.py --input "<文章.md>"` —— 微信兼容 HTML，无 `{{...}}` 残留；
4. `python scripts/publish-wechat.py --input "<文章.md>" --dry-run` —— 核对账号/标题/图片清单；正式发布必须先得到用户确认；
5. 图片锚点回填：文章位于已有系列目录内 → 并入该系列素材库.md 对应条目（封面/正文图文件名 + 锚点说明，写法同系列 17–20 课）；完全独立的单篇 → 可在「参考」前加可选「配图登记」小节，不想落盘则写进对话；
6. 收尾产物只应有：文章 .md、assets/ 图片、（可选）html/、（若发布）发布记录。

## 与系列模式差异速查

| 差异点 | 系列模式 | 单篇模式 |
| --- | --- | --- |
| frontmatter lesson | 必填 | 无 |
| 「下一步」章节 | 必设 | 不设（以延伸阅读收尾） |
| 系列规划.md / 素材库.md | 必建 | 不建 |
| 回填 | 进度表 + 合集 + 素材库三处必做 | 仅图片锚点登记（系列目录内必做，独立单篇可选） |
| 配图校验 | check-images.mjs（默认） | check-images.mjs --strict |
| 升级为系列 | — | 补建规划.md + 素材库.md + lesson + 「下一步」后继续 |
```

- [ ] **Step 2: 校验文件**

Run: `Test-Path references/single-mode.md`
Expected: `True`。

- [ ] **Step 3: Commit**

```bash
git add references/single-mode.md
git commit -m "docs: 新增单篇模式流程 references/single-mode.md"
```

---

### Task 3: SKILL.md 加模式路由、执行纪律与单篇入口

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: 更新 description（frontmatter 首行）**

将现有 description 替换为：

```yaml
description: 从零基础起步的系列教程（学习路径）或单篇文章写作技能。当用户要求写「从零开始学 XXX」「零基础入门 XXX」「XXX 从入门到进阶」类系列教程、需要先规划学习路径再逐篇成文，或只给定标题写一篇独立文章/公众号文章时使用；入口自动路由系列模式与单篇模式（无法判断默认单篇）。适用于任何主题（编程、语言、乐器、理财、运动、学科知识等），不限于代码类。铁律：动手写作前必须先做 web search 收集完整材料，素材不齐不写。
```

- [ ] **Step 2: 在 `# 从零开始学 XXX（From Zero Tutorial）` 标题后插入路由章节**

定位原文行：

```
# 从零开始学 XXX（From Zero Tutorial）

## 这个技能是干什么的
```

替换为：

```
# 从零开始学 XXX（From Zero Tutorial）

## 模式路由（先读这里）

本技能支持两种模式：**系列模式**（多篇教程，默认主流程）与**单篇模式**（给定标题写一篇文章）。收到请求先判断：

- **系列模式**：请求含「系列 / 从零开始学 / 零基础入门 / 第 N 篇 / 规划 / 多篇 / 合集 / 课程 / 进阶 / 续篇」，或「先写一篇、后面做成系列」→ 走下方「系列模式：七步流程」；
- **单篇模式**：请求含「写一篇 / 一篇文章 / 单篇 / 标题是 / 公众号文章 / 只写 XX / 独立文章」，或无法判断（默认）→ 读 [references/single-mode.md](references/single-mode.md)，按单篇五步执行；
- 两套信号都出现 → 系列模式。

### 执行纪律（防串模式）

- 单篇模式：不建系列规划.md、不建素材库.md、frontmatter 不写 lesson、正文不写「下一步」、收尾不回填三处、配图校验用 `check-images.mjs --strict`；
- 系列模式：每篇必须 lesson 与「下一步」、收尾回填三处必做、配图校验不用 --strict；
- 切换：单篇 → 系列（用户说「继续写下一篇 / 扩成系列」）时补建系列规划.md 与素材库.md，已有文章补 lesson 与「下一步」，转为系列第 1 篇继续；系列 → 单篇按单篇收尾。

## 这个技能是干什么的
```

- [ ] **Step 3: 标注系列七步归属（最小改动）**

定位原文行 `## 七步流程`，替换为 `## 系列模式：七步流程`。

- [ ] **Step 4: 核对**

Run: `Select-String -Path SKILL.md -Pattern "模式路由","references/single-mode.md","系列模式：七步流程" | Select-Object LineNumber`
Expected: 三处命中，行号递增。

- [ ] **Step 5: Commit**

```bash
git add SKILL.md
git commit -m "docs: SKILL.md 增加系列/单篇模式路由与执行纪律"
```

### Task 4: references/article.md 加模式差异标注

**Files:**
- Modify: `references/article.md`

- [ ] **Step 1: frontmatter 小节前插入模式说明**

定位原文行（frontmatter 代码块起始）：

```
### frontmatter

```yaml
---
title: XXX 零基础入门 · NN …
```

替换为：

```
### frontmatter

**模式差异**：本文档是两种模式共享的写作规范。系列模式按下方 frontmatter（含 lesson）；单篇模式用 [assets/templates/article-single-template.md](../assets/templates/article-single-template.md)，frontmatter 无 lesson，正文不设「下一步」，其余规范一致。

```yaml
---
title: XXX 零基础入门 · NN …
```

- [ ] **Step 2: 标题小节标注单篇**

定位原文行（标题统一「XXX 零基础入门 · NN：…」，主标题包含主题关键词……），在该句前插入：

```
（系列模式标题统一「XXX 零基础入门 · NN：…」；单篇模式直接用用户给定标题，同样要求含主题关键词。）
```

- [ ] **Step 3: 下一步小节标注**

定位原文行：

```
### 下一步

用 wikilink 指向下一课，写清「第 NN 课：一句话预告」。
```

替换为：

```
### 下一步

（系列模式必设；单篇模式不设本小节，以「延伸阅读」收尾。）

用 wikilink 指向下一课，写清「第 NN 课：一句话预告」。
```

- [ ] **Step 4: 核对**

Run: `Select-String -Path references/article.md -Pattern "模式差异","article-single-template.md","系列模式必设" | Select-Object LineNumber`
Expected: 三处命中。

- [ ] **Step 5: Commit**

```bash
git add references/article.md
git commit -m "docs: article.md 标注系列/单篇模式差异"
```

---

### Task 5: 新增单篇模板并指引系列模板

**Files:**
- Create: `assets/templates/article-single-template.md`
- Modify: `assets/templates/article-template.md`

- [ ] **Step 1: 写入单篇模板全文**

将以下内容原样保存为 `assets/templates/article-single-template.md`（UTF-8）：

```markdown
> 单篇模式专用模板（见 references/single-mode.md 与 references/article.md）。标题用用户给定标题；
> frontmatter 无 lesson；正文不写「下一步」；知识/介绍类只用「正文 → 参考」，操作/教程类加
> 「本节难点/要点速记 → 动手任务 → 完成标志 → Q&A」。

---
title: 用户给定的标题
subtitle: 一句有钩子的副标题
tags: [主题, 教程]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: [v2 完成]
cover: assets/<封面文件名>.png
style:   # 可选：图片风格 slug（封面生成后回填，见 references/images.md）
---

> 副标题：…
> 作者：…

![封面：本课主题一句话](assets/<封面文件名>.png)

## 一、场景化开场

信息类：用真实画面、故事或对话开场，把读者拉进场景。禁止「XXX 是什么」式教科书开场。
操作类：从「你打开电脑/拿起工具后会看到什么」开始。

## 二、正文

（概念 + 步骤/示例 + 讲解；术语第一次出现给一句话解释；至少 1 个真实案例、1 组数据表、误区澄清、延伸阅读；配图紧跟对应文字。）

## 本节难点（仅操作类按需）

① 「新手会问的原话？」——答案要点

## 要点速记（仅操作类按需）

① … ② … ③ …

## 动手任务（仅操作类）

（具体、可完成、有产出；需要硬件/账号/付费的单独标注。）

## 完成标志（仅操作类）

1. …
2. …

## 常见问题 Q&A（按需）

**Q：新手会问的原话？**
A：…

## 参考

- 官方文档/来源链接（可核实）

## 配图登记（可选）

- 封面：assets/<封面文件名>.png（图：…）
- 正文图：assets/<正文图文件名>.png（图：…，位于第 X 节）
```

- [ ] **Step 2: 系列模板加指引**

定位 assets/templates/article-template.md 首行（模板说明），在该行后追加一行：

```
> 单篇模式请改用 [article-single-template.md](article-single-template.md)（无 lesson、无「下一步」）。
```

- [ ] **Step 3: 核对**

Run: `Test-Path assets/templates/article-single-template.md`
Expected: `True`。

Run: `Select-String -Path assets/templates/article-template.md -Pattern "article-single-template.md"`
Expected: 命中 1 处。

- [ ] **Step 4: Commit**

```bash
git add assets/templates/article-single-template.md assets/templates/article-template.md
git commit -m "docs: 新增单篇文章模板并指引系列模板"
```

---

### Task 6: 单篇链路端到端 + 隔离校验

**Files:**
- Test: 临时目录（不入库）

- [ ] **Step 1: 造单篇样本并生成封面**

```powershell
$base = Join-Path $env:TEMP "fzt-single-e2e"
Remove-Item -LiteralPath $base -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Join-Path $base "assets") | Out-Null
$mdLines = @(
  "---",
  "title: 测试：FRC 电机的 Phoenix 配置",
  "subtitle: 用 Tuner X 设 ID 与看状态",
  "tags: [frc, 教程]",
  "created: 2026-09-02",
  "updated: 2026-09-02",
  "status: [v2 完成]",
  "cover: assets/single-cover.png",
  "---",
  "",
  "> 副标题：用 Tuner X 设 ID 与看状态",
  "> 作者：星启",
  "",
  "![封面：Phoenix 配置](assets/single-cover.png)",
  "",
  "## 一、场景开场",
  "正文测试内容。"
)
$md = $mdLines -join [Environment]::NewLine
Set-Content -LiteralPath (Join-Path $base "sample.md") -Value $md -Encoding UTF8
node scripts/cover-generator/generate.mjs --input (Join-Path $base "sample.md") --width 1068 --height 455 --out (Join-Path $base "assets\single-cover.png")
```

Expected: 日志含 `title 来源：frontmatter title` 与 `[OK]`，生成 assets/single-cover.png。

- [ ] **Step 2: 造一张正文图并插入引用**

```powershell
node scripts/cover-generator/generate.mjs --style chalk --template "scripts/cover-generator/templates/figures/card-knowledge.html" --title "版本匹配" --tag "易错点" --set BODY="固件年份与 API 年份要一致。" --out (Join-Path $base "assets\body.png")
```

再用文本替换把 sample.md 中 `## 一、场景开场` 与 `正文测试内容。` 之间插入一行 `![图：版本匹配说明](assets/body.png)`（把 `## 一、场景开场` 后紧跟的段落替换为 `![图：版本匹配说明](assets/body.png)` 开头的新段落）。

- [ ] **Step 3: 校验链（--strict + 厚度 + HTML + dry-run）**

Run: `node scripts/check-images.mjs --root <base> --strict`
Expected: `[OK] 配图检查通过`（封面+正文图齐全，无 lesson 也被强制校验通过）。

Run: `node scripts/check-articles.mjs --root <base>`
Expected: 退出码 1，输出 `字数不足`（样本未写满 3500 字，属预期；真实写作按 3500–8000 达标）。

Run: `python scripts/md-to-html.py --input <base>/sample.md --theme refined-blue`
Expected: 输出含 refined-blue，生成 html/sample.html，无 `{{...}}`。

Run: `python scripts/publish-wechat.py --input <base>/sample.md --dry-run`
Expected: `[标题] 测试：FRC 电机的 Phoenix 配置`（frontmatter title），4 项流程预览，退出码 0。

- [ ] **Step 4: 隔离校验（未产生系列专属产物）**

Run: `Get-ChildItem <base> -Filter "*规划*.md"; Get-ChildItem <base> -Filter "素材库*.md"; Select-String -Path <base>/sample.md -Pattern "^lesson:"`
Expected: 三项均无输出（未建规划/素材库；frontmatter 无 lesson）。

- [ ] **Step 5: 系列回归**

Run: `node scripts/check-images.mjs --root "C:\myobsidian\30 - myprojects\FRC学习教程" | Select-String -Pattern "\[结果\]"`
Expected: `[结果] 共 43 个问题（断链 1、未用图 25、缺封面 17、缺正文图 0）`（与改动前一致；21-Phoenix.md 不在问题列表）。

Run: `node scripts/check-articles.mjs --root "C:\myobsidian\30 - myprojects\FRC学习教程"`
Expected: `[OK] 内容厚度检查通过`。

- [ ] **Step 6: 清理临时目录**

```powershell
Remove-Item -LiteralPath <base> -Recurse -Force
```

无 commit：临时产物不入库；若脚本产物误入工作区先清理再继续。

---

### Task 7: 文档自检与收尾

**Files:**
- Modify: 无（仅检查）

- [ ] **Step 1: 对照 spec 覆盖检查**

逐项核对（全部命中才算完成）：
- [ ] spec 第 2 节"三层文档组织"：SKILL.md 路由（Task 3）、single-mode.md（Task 2）、系列七步原位（Task 3 Step 3）
- [ ] spec 第 3 节矩阵"check-images 参数隔离"：--strict（Task 1）
- [ ] spec 第 4 节单篇五步：写入 single-mode.md（Task 2）
- [ ] spec 第 5 节路由规则与切换：SKILL.md（Task 3）
- [ ] spec 第 7 节文件清单：article.md（Task 4）、两个模板（Task 5）
- [ ] spec 第 8 节 --strict 行为：Task 1 Step 4 已断言
- [ ] spec 第 9 节单篇模板 frontmatter：Task 5 Step 1
- [ ] spec 第 11 节验证：Task 6（端到端+隔离+回归）
- [ ] spec 第 12 节"不迁移七步正文"：Task 3 仅标注标题，未移动正文

- [ ] **Step 2: 确认 git 历史**

Run: `git log --oneline -8`
Expected: 本计划各 Task 的 commit 依次出现，且未覆盖上一轮 generate.mjs --input 改动。

- [ ] **Step 3: 最终状态说明**

输出最终报告：改动文件清单、--strict 用法、单篇模式入口位置、系列回归结果。


## 执行期修订记录

- 2026-09-02：Task 6 验证发现 check-articles.mjs 默认只校验带 lesson 文章（样本 0 篇恒通过），与 Task 6 Step 3 预期不符。修订：check-articles.mjs 增加 `--strict`（同 check-images 模式），references/single-mode.md 第 5 步与 SKILL.md 执行纪律改用 `--strict`；spec 追加 v4 修订记录。Task 6 Step 3 的 check-articles 断言改为：默认 `[OK] 0 篇`（行为不变）；`--strict` 时样本 `字数不足：36 字` 退出码 1。
