# 从零开始学 XXX（From Zero Tutorial）

一个把「零基础系列教程」当作学习产品来生产的 Agent Skill：适用于 Codex、Claude Code、千问办公、CodeBuddy、Trae 等主流 AI 工具。先弄清读者和终点，再规划学习路径，再逐篇写作。每篇都能动手、有完成标志，读者跟着走完就有真实能力。

## 目录

1. [这个 Skill 是干嘛的？](#1-这个-skill-是干嘛的)
2. [它解决什么问题](#2-它解决什么问题)
3. [核心特性](#3-核心特性)
4. [使用效果](#4-使用效果)
   - [4.1 系列文章规划示例效果](#41-系列文章规划示例效果)
   - [4.2 示例公众号文章显示效果](#42-示例公众号文章显示效果)
5. [安装到各 AI 工具](#5-安装到各-ai-工具)
   - [5.1 技能目录对照表](#51-技能目录对照表)
   - [5.2 命令行安装示例](#52-命令行安装示例)
6. [在各 AI 工具中使用示例](#6-在各-ai-工具中使用示例)
   - [6.1 触发示例](#61-触发示例)
   - [6.2 执行流程](#62-执行流程)
7. [快速开始](#7-快速开始)
   - [7.1 安装依赖](#71-安装依赖)
   - [7.2 复制配置并填写凭据](#72-复制配置并填写凭据)
   - [7.3 使用示例](#73-使用示例)
     - [7.3.1 转 HTML](#731-转-html)
     - [7.3.2 配图与内容校验](#732-配图与内容校验)
     - [7.3.3 发布到公众号草稿箱](#733-发布到公众号草稿箱)
8. [目录结构](#8-目录结构)
9. [隐私与安全](#9-隐私与安全)
10. [许可证](#10-许可证)

## 1. 这个 Skill 是干嘛的？

你是不是有个想法：想写一套「从零开始学 XXX」的系列教程，比如 Python、摄影、Excel、理财……但真动笔时，脑子里只有主题，不知道：

- 该分几课？每课讲什么？
- 开头怎么讲才不劝退小白？
- 数据不敢乱编，官方资料又懒得查？
- 写到后面忘了前面，前后矛盾？
- 配图、排版、发公众号又是一堆杂活？

**这个 Skill 就是替你把这些「烦人活」全包了。**

你只要告诉 AI 一句：「我想写『从零开始学 Git』系列」，它就会自动——

1. **先帮你做市场调研**（网上搜一圈，看看同类教程怎么写的，避开坑）；
2. **规划完整学习路径**（几课、每课目标、学完能干嘛，像课程大纲一样清晰）；
3. **建立「素材库」**（术语解释、官方链接、真实案例，全部双源核实，不编造）；
4. **一篇一篇写正文**（每篇都有动手环节、完成标志，读者跟着做就有收获）；
5. **自动配图**（封面、正文插图，33 种风格随便选，不用你去找图）；
6. **校验内容**（字数够不够、图片有没有漏、逻辑通不通）；
7. **一键转成微信公众号文章**（排版适配、封面比例自动切、Mermaid 图表转图片）；
8. **甚至帮你发布到公众号草稿箱**（防重复发布，图片自动上传复用）。

全程你只需要说「开始」，中间可以随时提修改意见，其他机械活儿 AI 全干。

## 2. 它解决什么问题

系列教程常见的坑：想到哪写到哪、默认读者有前置知识、只讲不练、数据编造、写完没人校验。本技能用一条强制流程把这些堵住：**取材先行 → 双源核实 → 规划路径 → 逐篇写作 → 动手验证 → 转 HTML →（可选）发布微信公众号草稿**。

## 3. 核心特性

- 七步流程：取材分析 → 系列规划 → 素材库 → 逐篇写作 → 验证回填 → 转 HTML → 发布微信；
- 十条设计原则：无门槛可学、每课有完成标志、术语首现一句话解释、官方资料优先、禁止编造案例与数据；
- 配图引擎：[scripts/cover-generator/](scripts/cover-generator/)，33 套风格的模板化封面/正文卡（HTML→PNG，Playwright 或本机 Edge/Chrome）；
- 微信适配：15 套主题的 md→HTML 转换、Mermaid 渲染为 PNG、封面 2.35:1 比例守卫；
- 公众号草稿发布/更新：防重复发布、UTF-8 中文原文发送、图片 CDN 复用；
- 自动化校验：配图一一对应（0 断链 / 0 未用图 / 缺封面 / 缺正文图）、内容厚度 3500-8000 字。

## 4. 使用效果

### 4.1 系列文章规划示例效果

![系列文章规划示例效果](images/系列文章规划示例效果.png)

**说明**：从零开始学系列的学习路径与课程规划。

### 4.2 示例公众号文章显示效果

![示例公众号文章显示效果](images/示例公众号文章显示效果.gif)

**说明**：微信公众号文章预览。

## 5. 安装到各 AI 工具

本技能不是某个 AI 工具的专属格式，而是标准 Agent Skill：目录名 `from-zero-tutorial`、根目录带 `SKILL.md`，Codex、Claude Code、千问办公、CodeBuddy、Trae、WorkBuddy、百度搭子、豆包工作等都能用。克隆或复制到对应工具的技能目录即可被识别（Windows 直接复制整个文件夹，Linux/macOS 也可用符号链接）。

### 5.1 技能目录对照表

| 工具 | 安装位置 / 方式 |
| --- | --- |
| Codex | 个人技能 `C:\Users\<你>\.codex\skills\from-zero-tutorial`（Linux/macOS：`~/.codex/skills/from-zero-tutorial`），或使用 Codex 的 skill 安装器 |
| Claude Code | 个人技能 `~/.claude/skills/from-zero-tutorial`；项目级放 `.claude/skills/` |
| CodeBuddy | 个人技能 `~/.codebuddy/skills/from-zero-tutorial`；项目级放 `.codebuddy/skills/` |
| Trae | 项目级 `.trae/skills/from-zero-tutorial`，或「设置 → Rules and Skills → 导入 SKILL.md」 |
| DeepSeek Harness | 放入 `$DSH_HOME/skills/from-zero-tutorial`；也可在 Web UI「设置 → 插件 → Skills」中从本仓库一键安装 |
| WorkBuddy | 个人技能 `~/.workbuddy/skills/from-zero-tutorial`（部分版本为 `C:\Users\<你>\WorkBuddy\Claw\skills\`，以官方文档为准），或通过 WorkBuddy 技能市场安装 |
| 阿里千问办公（QwenWork） | 个人技能 `~/.qwenworkcn/skills/from-zero-tutorial`（Windows：`C:\Users\<你>\.qwenworkcn\skills\`），或在千问办公「技能 → 安装技能」上传 SKILL.md 及辅助文件 |
| 百度搭子（DuMate） | 客户端「技能 → 安装技能」导入含 SKILL.md 的 zip 压缩包（支持拖入 URL）；技能广场可安装内置技能 |
| 豆包工作 | 打开 [豆包工作](https://www.doubao.com/work) → 「技能·连接器·伙伴」安装，或自定义导入含 SKILL.md 的技能包（可将本仓库打包为 zip 导入） |

### 5.2 命令行安装示例

一条命令示例（Claude Code，Linux/macOS）：

```bash
mkdir -p ~/.claude/skills
git clone --depth 1 https://github.com/chengwind198/from-zero-tutorial.git ~/.claude/skills/from-zero-tutorial
```

其他工具同理：把仓库复制/克隆到上表对应目录，目录名保持 `from-zero-tutorial`，各工具会按 [SKILL.md](SKILL.md) 的 description 自动匹配触发。

## 6. 在各 AI 工具中使用示例

安装后无需额外配置，直接对 AI 说需求即可——技能描述包含「从零开始学 XXX / 零基础入门 / 从入门到进阶」等关键词时会自动匹配：

### 6.1 触发示例

- **Codex**：`用 from-zero-tutorial 写「从零开始学 Python」系列教程：先做学习路径规划，再写第一篇「为什么是 Python」。`
- **Claude Code**：`使用 from-zero-tutorial 技能，为「零基础入门 Git」规划一个 8 课系列，然后写第一课。`
- **CodeBuddy**：`用 from-zero-tutorial 写「零基础入门 React」系列：先规划学习路径，再写第一篇。`
- **Trae**：`使用 from-zero-tutorial 技能，为「从零开始学视频剪辑」做系列规划并写第一课。`
- **WorkBuddy**：`用 from-zero-tutorial 写「零基础入门 Excel 函数」系列：先规划学习路径，再写第一篇。`
- **千问办公（QwenWork）**：`使用 from-zero-tutorial 技能，为「从零开始学摄影」做系列规划并写第一课。`

### 6.2 执行流程

触发后技能会按七步流程自动执行：web search 取材 → 系列规划 → 素材库 → 逐篇写作 → 配图与校验 → 转 HTML（发布按需），全程无需手动分步；关键数据会做双源核实，案例与数据禁止编造。

## 7. 快速开始

### 7.1 安装依赖

- Python 3 + `pip install markdown beautifulsoup4 pyyaml requests`；
- Node.js 18+（配图生成需要；Playwright 可选，未装则用本机 Edge/Chrome）。

### 7.2 复制配置并填写凭据

```powershell
Copy-Item config.yaml.example config.yaml
# 编辑 config.yaml，填入 AppID / AppSecret
```

### 7.3 使用示例

在技能根目录执行，`--input` 传你自己的文章路径。

#### 7.3.1 转 HTML

```powershell
python scripts/md-to-html.py --input "01-数学竞赛是什么.md" --theme refined-blue
```

#### 7.3.2 配图与内容校验

在系列目录运行：

```powershell
node scripts/check-images.mjs --root "你的系列目录"
node scripts/check-articles.mjs --root "你的系列目录"
```

#### 7.3.3 发布到公众号草稿箱

先干跑核对账号/标题/图片：

```powershell
python scripts/publish-wechat.py --input "01-数学竞赛是什么.md" --dry-run
```

完整用法见 [SKILL.md](SKILL.md)（技能主文档：铁律、七步流程、设计原则）与 [references/](references/)（规划 / 单篇写作 / 配图 / 发布规范）。

## 8. 目录结构

| 路径 | 说明 |
| --- | --- |
| [SKILL.md](SKILL.md) | 技能主文档 |
| [references/](references/) | 规划、单篇写作、配图、发布的详细规范 |
| [assets/templates/](assets/templates/) | 系列规划、素材库、文章模板 |
| [scripts/](scripts/) | md→HTML、微信发布/更新、配图与内容校验脚本 |
| [scripts/cover-generator/](scripts/cover-generator/) | 模板化配图引擎（33 套风格 + 正文卡模板） |
| [themes/](themes/) | 15 套微信 HTML 主题 |
| [config.yaml.example](config.yaml.example) | 发布配置模板（真实配置 `config.yaml` 不入库） |
| [draft-records.example.json](draft-records.example.json) | 草稿记录空模板（真实记录由脚本自动创建，不入库） |

## 9. 隐私与安全

- `config.yaml` 含公众号 AppSecret，已加入 `.gitignore`，**绝不提交**；
- `draft-records.json` / `draft-records.backup.json` 含本机路径与图片映射，是本地运行数据，已加入 `.gitignore`，脚本会自动创建；
- 写作铁律：关键数据双源核实、禁止编造案例/数据/对话；截图注意裁掉用户名、路径、密钥。

## 10. 许可证

本项目采用 [Apache License 2.0](LICENSE) 开源（Copyright 2026 chengwind198）。