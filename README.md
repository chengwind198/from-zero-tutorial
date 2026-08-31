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

暂未指定，发布到 GitHub 前请补充 LICENSE。
