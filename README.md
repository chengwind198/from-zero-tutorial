# 从零开始学 XXX（From Zero Tutorial）

一个把「零基础系列教程」当作学习产品来生产的 Codex Agent Skill：先弄清读者和终点，再规划学习路径，再逐篇写作。每篇都能动手、有完成标志，读者跟着走完就有真实能力。

## 它解决什么问题

系列教程常见的坑：想到哪写到哪、默认读者有前置知识、只讲不练、数据编造、写完没人校验。本技能用一条强制流程把这些堵住：**取材先行 → 双源核实 → 规划路径 → 逐篇写作 → 动手验证 → 转 HTML →（可选）发布微信公众号草稿**。

## 核心特性

- 七步流程：取材分析 → 系列规划 → 素材库 → 逐篇写作 → 验证回填 → 转 HTML → 发布微信；
- 十条设计原则：无门槛可学、每课有完成标志、术语首现一句话解释、官方资料优先、禁止编造案例与数据；
- 配图引擎：[scripts/cover-generator/](scripts/cover-generator/)，33 套风格的模板化封面/正文卡（HTML→PNG，Playwright 或本机 Edge/Chrome）；
- 微信适配：15 套主题的 md→HTML 转换、Mermaid 渲染为 PNG、封面 2.35:1 比例守卫；
- 公众号草稿发布/更新：防重复发布、UTF-8 中文原文发送、图片 CDN 复用；
- 自动化校验：配图一一对应（0 断链 / 0 未用图 / 缺封面 / 缺正文图）、内容厚度 3500-8000 字。

## 安装到各 AI 工具

本项目是标准 Agent Skill：目录名 `from-zero-tutorial`、根目录带 `SKILL.md`，克隆或复制到对应工具的技能目录即可被识别（Windows 直接复制整个文件夹，Linux/macOS 也可用符号链接）。

| 工具 | 安装位置 / 方式 |
| --- | --- |
| Codex | 个人技能 `C:\Users\<你>\.codex\skills\from-zero-tutorial`（Linux/macOS：`~/.codex/skills/from-zero-tutorial`），或使用 Codex 的 skill 安装器 |
| Claude Code | 个人技能 `~/.claude/skills/from-zero-tutorial`；项目级放 `.claude/skills/` |
| Trae | 项目级 `.trae/skills/from-zero-tutorial`，或「设置 → Rules and Skills → 导入 SKILL.md」 |
| DeepSeek Harness | 放入 `$DSH_HOME/skills/from-zero-tutorial`；也可在 Web UI「设置 → 插件 → Skills」中从本仓库一键安装 |
| WorkBuddy | 个人技能 `~/.workbuddy/skills/from-zero-tutorial`（部分版本为 `C:\Users\<你>\WorkBuddy\Claw\skills\`，以官方文档为准），或通过 WorkBuddy 技能市场安装 |
| 阿里千问办公（QwenWork） | 个人技能 `~/.qwenworkcn/skills/from-zero-tutorial`（Windows：`C:\Users\<你>\.qwenworkcn\skills\`），或在千问办公「技能 → 安装技能」上传 SKILL.md 及辅助文件 |
| 百度搭子（DuMate） | 客户端「技能 → 安装技能」导入含 SKILL.md 的 zip 压缩包（支持拖入 URL）；技能广场可安装内置技能 |
| 豆包工作 | 打开 [豆包工作](https://www.doubao.com/work) → 「技能·连接器·伙伴」安装，或自定义导入含 SKILL.md 的技能包（可将本仓库打包为 zip 导入） |

一条命令示例（Claude Code，Linux/macOS）：

```bash
mkdir -p ~/.claude/skills
git clone --depth 1 https://github.com/chengwind198/from-zero-tutorial.git ~/.claude/skills/from-zero-tutorial
```

其他工具同理：把仓库复制/克隆到上表对应目录，目录名保持 `from-zero-tutorial`，各工具会按 [SKILL.md](SKILL.md) 的 description 自动匹配触发。

## 在 Codex / Claude Code 中使用示例

安装后无需额外配置，直接对 AI 说需求即可——技能描述包含「从零开始学 XXX / 零基础入门 / 从入门到进阶」等关键词时会自动匹配：

- **Codex**：`用 from-zero-tutorial 写「从零开始学 Python」系列教程：先做学习路径规划，再写第一篇「为什么是 Python」。`
- **Claude Code**：`使用 from-zero-tutorial 技能，为「零基础入门 Git」规划一个 8 课系列，然后写第一课。`
- **WorkBuddy**：`用 from-zero-tutorial 写「零基础入门 Excel 函数」系列：先规划学习路径，再写第一篇。` 
- **千问办公（QwenWork）**：`使用 from-zero-tutorial 技能，为「从零开始学摄影」做系列规划并写第一课。`

触发后技能会按七步流程自动执行：web search 取材 → 系列规划 → 素材库 → 逐篇写作 → 配图与校验 → 转 HTML（发布按需），全程无需手动分步；关键数据会做双源核实，案例与数据禁止编造。
## 快速开始

1. 安装依赖：

   - Python 3 + `pip install markdown beautifulsoup4 pyyaml requests`；
   - Node.js 18+（配图生成需要；Playwright 可选，未装则用本机 Edge/Chrome）。

2. 复制配置模板并填写公众号凭据：

   ```powershell
   Copy-Item config.yaml.example config.yaml
   # 编辑 config.yaml，填入 AppID / AppSecret
   ```

3. 使用示例（在技能根目录执行，`--input` 传你自己的文章路径）：

   ```powershell
   # 文章 → 微信兼容 HTML（主题可指定，默认随机）
   python scripts/md-to-html.py --input "01-数学竞赛是什么.md" --theme refined-blue

   # 配图与内容校验（在系列目录运行）
   node scripts/check-images.mjs --root "你的系列目录"
   node scripts/check-articles.mjs --root "你的系列目录"

   # 发布到公众号草稿箱（先干跑核对账号/标题/图片）
   python scripts/publish-wechat.py --input "01-数学竞赛是什么.md" --dry-run
   ```

完整用法见 [SKILL.md](SKILL.md)（技能主文档：铁律、七步流程、设计原则）与 [references/](references/)（规划 / 单篇写作 / 配图 / 发布规范）。

## 目录结构

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

## 隐私与安全

- `config.yaml` 含公众号 AppSecret，已加入 `.gitignore`，**绝不提交**；
- `draft-records.json` / `draft-records.backup.json` 含本机路径与图片映射，是本地运行数据，已加入 `.gitignore`，脚本会自动创建；
- 写作铁律：关键数据双源核实、禁止编造案例/数据/对话；截图注意裁掉用户名、路径、密钥。

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 开源（Copyright 2026 chengwind198）。
