---
name: from-zero-tutorial
description: 从零基础起步的系列教程（学习路径）或单篇文章写作技能。当用户要求写「从零开始学 XXX」「零基础入门 XXX」「XXX 从入门到进阶」类系列教程、需要先规划学习路径再逐篇成文，或只给定标题写一篇独立文章/公众号文章时使用；入口自动路由系列模式与单篇模式（无法判断默认单篇）。适用于任何主题（编程、语言、乐器、理财、运动、学科知识等），不限于代码类。铁律：动手写作前必须先做 web search 收集完整材料，素材不齐不写。
---

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

把「零基础系列教程」当作一个学习产品来生产：先弄清读者和终点，再规划路径，再逐篇写作。每篇都能动手、有完成标志，读者跟着走完就有真实能力。产出三件套：

- **系列规划.md**：地图——读者定位、设计原则、学习路径总览、每课详案、术语表、进度表；
- **素材库.md**：弹药——真实案例、截图、数据与来源、故事访谈、试读记录；
- **每篇文章**：路——固定结构、可动手、可验证。

适用于任何主题，不假设读者有任何前置知识，所有术语第一次出现给一句话解释。

## 铁律（违反即返工）

1. **取材先行**：任何写作动作之前，必须先做 web search 收集完整材料——主题全景、官方/权威资料、案例数据、读者常见问题、现有内容缺口。材料不齐不写；禁止编造案例、数据、对话；无法核实的内容要么不写，要么明确标注「以官方为准」并附入口链接。
2. **双源核实**：关键数据（规模、版本、日期、价格、事实性陈述）至少两个独立来源交叉校验，来源与核验日期登记进素材库。
3. **写完必验**：作者按文中流程完整走一遍，再找一位真正的目标读者试读，卡点原话写进 Q&A。
4. **整篇一次跑完（回合纪律）**：用户要求写某一篇时，从取材到成文必须一次完成，中间不结束回合。取材（web search）结束不是停止点——搜索完立即继续写作；素材不齐就继续补搜，不要停下来问用户或只汇报进度。同一回合尽量推进到「转 HTML」（发布按需）；每完成一个里程碑（取材、封面、正文、配图、校验、回填、HTML）发一条简短的 commentary 更新即可，阶段性汇报不等于最终回复。

## 系列模式：七步流程

### 第一步：取材与分析（web search 强制）

先检索，后判断：

- 用 web search 摸清主题全景：这个领域是什么、官方/权威资料在哪、主流学习路径、常见误区、中文/本地可用资源、现有教程缺什么；
- 关键事实与数据双源核实，连同来源链接、核验日期一起记入素材库；
- 基于检索结果明确：学完这个系列读者能独立完成什么（终点能力）；目标读者是谁；需要什么前置知识（一律按无设计）；哪些步骤不需要硬件/账号/付费就能完成；
- 判断单系列还是拆子系列：读者群体差异过大时拆（例如「使用」与「开发」两类人该学的东西完全不同）。

> **取材完成即继续**：web search 结束不是停止点。素材齐了直接进入下一步；不齐就继续做针对性搜索（每篇控制在 2-4 轮，够用为准，避免上下文膨胀）。生图、转 HTML、发布等需要本机浏览器或命令的操作，如遇沙箱要求授权，主动申请授权后继续，不要因为等待授权而结束回合。

### 第二步：规划系列

生成「系列规划.md」。用 [assets/templates/series-plan-template.md](assets/templates/series-plan-template.md) 起步，规范见 [references/planning.md](references/planning.md)。规划文档必须包含：

- 读者定位、系列设计原则、写作规范；
- 学习路径总览表：阶段 / 课 / 一句话目标 / 阅读时长 / 实践时长 / 适合人群；
- 每课详案：建议标题与副标题、正文要点、动手任务、完成标志、常见坑；
- 术语表、官方资源与下载地址汇总、配图映射、执行进度表；
- 顺序原则：先全景、后动手、再深挖；每课只引入一个新难点；设 2-3 个「做完就有能力」的里程碑课。

### 第三步：建素材库

创建「素材库.md」（模板见 [assets/templates/material-bank-template.md](assets/templates/material-bank-template.md)），把取材阶段的来源、链接、核验日期、截图、案例登记入库。每篇动笔前从库里取料，写完把新素材回填。

### 第四步：逐篇写作

按 [references/article.md](references/article.md) 与 [assets/templates/article-template.md](assets/templates/article-template.md) 写每篇：

- 动笔前先按该课详案里的「素材清单」做一轮针对性 web search 补料，素材齐了才写；
- 章节按文章类型匹配（不是固定套餐）：基础件是 frontmatter、标题+副标题、正文、参考、下一步；知识/介绍类只用这些，操作/教程类才加「本节难点/要点速记 → 动手任务 → 完成标志 → Q&A」，见 [references/article.md](references/article.md)；
- 内容厚度：每篇正文 3500-8000 字（知识/介绍类按信息块骨架充实：案例、数据表、误区澄清、延伸阅读；厚度来自素材，不注水）；
- 去 AI 味：场景化开场、一稿二改、直接说人话，不写总结句和套话。

### 第五步：验证与回填

- 作者按文中流程完整走一遍：命令可执行、步骤不迷路、截图与版本一致；
- 配图强制：每篇（frontmatter 带 lesson 的文章）必须同时有封面图和正文配图（至少各一张），运行 [scripts/check-images.mjs](scripts/check-images.mjs) 验证 0 断链、0 未用图、0 缺封面、0 缺正文图；缺任一视为未完成；
- 内容厚度：每篇正文 3500-8000 字，运行 [scripts/check-articles.mjs](scripts/check-articles.mjs) 验证；字数不足或超长视为未完成；
- 目标读者试读，卡点原话写进 Q&A；
- 回填三处：规划进度表、系列合集/索引、素材库；漏回填视为未完成。

### 收尾执行约定（第六、七步的执行时机）

本技能采用「约定式收尾」：每篇文章进入 v2 完成状态后，作者默认继续执行第六步（转 HTML）和第七步的发布 dry-run（核对账号、标题、图片、留言设置），并把核对结果汇报给用户；**正式调用发布 API 属于外部操作，必须先得到用户明确确认**（如用户说「发布」「确认发布」）再执行。若用户要求其他模式（例如每篇都自动正式发布，或发布前一律暂停询问），以用户要求为准。

### 第六步：转 HTML（每篇完成后执行）

把文章转成微信兼容、带主题排版的 HTML（规范见 [references/publishing.md](references/publishing.md)）。以下命令默认在**本技能根目录（SKILL.md 所在文件夹）**执行，`--input` 传你自己的文章路径；换机器时无需改命令，只要先 `cd` 到本技能目录即可：

```powershell
python scripts/md-to-html.py --input "01-数学竞赛是什么.md" --dry-run
python scripts/md-to-html.py --input "01-数学竞赛是什么.md" --theme refined-blue
```

- 主题选择：`--theme <slug>` 指定（themes/*.json 共 15 套）；未指定随机选一套；
- 转 HTML 参数全部走命令行：`--theme` / `--html-dir`（默认 html）/ `--mermaid-cmd`（默认 mmdc），config.yaml 只管公众号发布；
- Mermaid 必须渲染成 PNG（`--mermaid-cmd mmdc`）；找不到渲染命令时转 HTML 会保留源码占位并警告，发布会中止；
- 转完检查：HTML 无 `{{...}}` 残留、无断图、正文图与封面引用完整（图片仍是本地相对路径，发布时上传替换）；
- 状态自动回写：转 HTML 成功后，文章 frontmatter 的 `status` 会自动追加「已生成html」。

### 第七步：发布到微信公众号（可选，按需执行）

首次发布前复制 [config.yaml.example](config.yaml.example) 为 config.yaml（`Copy-Item config.yaml.example config.yaml`），填入自己的公众号 AppID/AppSecret——config.yaml 含密钥，已被 .gitignore 忽略、不入版本库；然后（同样在技能根目录执行）：

```powershell
python scripts/publish-wechat.py --input "01-数学竞赛是什么.md" --dry-run
python scripts/publish-wechat.py --input "01-数学竞赛是什么.md"
```

- 流程：获取 access_token → 上传正文图片（/media/uploadimg）→ 上传封面（thumb 素材）→ 创建草稿（/draft/add）；
- 标题来源：草稿 `title` 默认取文章 frontmatter 的 `title`（可用 `--title` 覆盖），摘要默认取 frontmatter `subtitle`（可用 `--digest` 覆盖）；
- 封面优先级：`--cover` > frontmatter `cover` > 文章第一张图；
- 缺图守卫：正文图上传失败默认中止，`--allow-missing-images` 才继续；
- 发布前必跑 `--dry-run` 核对账号、标题、图片清单；
- 留言设置：`config.yaml` 的 `publish.need_open_comment`（默认 true，打开留言）与 `only_fans_can_comment`（默认 false，所有人可留言）会写入草稿接口，发布/更新草稿均生效；**「自动精选留言」微信没有公开 API**，只能到公众号后台人工开启（功能/互动 → 留言管理 → 自动精选），发布成功后脚本会打印提醒；
- 状态自动回写：发布成功后，文章 frontmatter 自动追加 `status` 标记「已发布草稿」，并写入 `published_at` / `wechat_media_id` / `wechat_title` / `wechat_digest` / `wechat_images`；
- 草稿详情（封面 media_id、图片 CDN 映射、文章路径等）自动存 `draft-records.json`，供更新草稿脚本使用；素材库不再手动回填发布信息；
- **防重复发布**：记录中已存在同标题草稿时，发布会默认中止并提示改用更新脚本（确认要另建草稿才加 `--duplicate-ok`）；
- **记录路径为相对路径**：`draft-records.json` 里文章/封面/图片路径均相对各记录的 `base_dir` 存储，换机器或移动目录时只需把 `base_dir` 改为新位置。

**更新/修复已发布的草稿**：

```powershell
# 列出已发布草稿记录
python scripts/update-wechat-draft.py --list

# 按标题关键词定位并更新（复用记录里的图片 CDN URL，重读文章 HTML）
python scripts/update-wechat-draft.py --key "别急着入坑"

# 按 media_id 更新，指定新标题/摘要或换封面
python scripts/update-wechat-draft.py --media-id <id> --title "新标题" --digest "新摘要" --cover assets/cover-03.png
```

- `--key` 匹配到多条草稿记录时会列出全部并要求用 `--media-id` 精确定位，避免更新错草稿；
- 正文图片优先复用发布时记录的 CDN URL（不重复上传）；文章改动后新增的本地图才会重新上传；
- 更新前若没有记录，脚本会拉取草稿现有内容并把 `\uXXXX` 乱码解码后重写（修复发布乱码场景）；
- 微信 `draft/update` 必须携带 `thumb_media_id`，脚本会自动复用原封面；
- 请求一律以 UTF-8 中文原文发送（`ensure_ascii=False`），避免微信把 `\uXXXX` 转义当字面文本存储。

## 十条设计原则（每课、每篇都要对照）

1. 取材先行、素材不齐不写；
2. 先全景、后动手、再深挖；
3. 无门槛可学：尽量不需要硬件/账号/付费，需要的单独标注；
4. 每课有完成标志，动手大于阅读；
5. 随用随讲、不假设读者，术语首现一句话解释；
6. 难度递进、一次只学一个新概念；
7. 官方/权威资料优先，系列是路线图不是参考书；
8. 去 AI 味：场景开场、一稿二改、说人话；
9. 双源核实、禁止编造；
10. 写后回填：进度表、合集、素材库同步更新。

## 配图方案

每篇至少一张示意图或截图。系列封面、章节头图这类「批量但统一」的图，推荐用**模板化配图**：HTML/CSS 模板 + 无头浏览器截图，把标题、分类、标签自动渲染成统一风格的图——零生成成本、品牌一致、完全可控。这是**通用 HTML→PNG 引擎**（[scripts/cover-generator/generate.mjs](scripts/cover-generator/generate.mjs)）：封面用 `--style`，文章里的知识卡/示意图等正文配图用 `--template` + `--set` 任意占位符。Obsidian 里可配合 Templater 在新笔记创建时自动出图。封面生成支持 `--input` 直接传文章 .md：标题/副标题/期号/分类/系列/风格缺省取文章 frontmatter（命令行显式参数优先），保证封面 title 与文章 header 的 `title` 一致，无需手动抄标题。

所有配图按统一目录存放（封面 `assets/cover-NN.png`、每课正文图 `assets/NN/` 一课一目录），正文引用与文件一一对应。**每篇系列文章必须同时有封面图和正文配图（至少各一张），缺封面或缺正文图都视为未完成**——发布前运行 [scripts/check-images.mjs](scripts/check-images.mjs) 验证 0 断链、0 未用图、0 缺封面、0 缺正文图。正文配图可用内置 figures 模板（card-flow / card-list / card-compare / card-knowledge）生成。方案、脚本、存放与锚点规范见 [references/images.md](references/images.md) 与 [scripts/cover-generator/](scripts/cover-generator/)。

**公众号封面尺寸（硬性）**：微信头条封面按 2.35:1 裁切（上传建议 1068×455，展示 900×383）。作为公众号发布用途的封面必须按 2.35:1 生成（`generate.mjs --width 1068 --height 455`），否则微信会裁掉左右边缘、文字可能被截；`publish-wechat.py` 发布前会检查封面宽高比，偏离 2.35:1 会警告或中止。1200×630 仅用于知识库头图与正文图，不能直接当公众号封面上传。详见 [references/images.md](references/images.md) 的「封面尺寸」一节。

封面生成支持**模板风格随机/路由**：`templates/manifest.json` 定义 33 个模板（default + 32 套风格，与 web-image 一一对应）。用户指定 `--style` 就按指定风格；**未指定时默认随机**——脚本从 33 套风格里随机选一套（`--random`，不传也默认随机），篇与篇不强求统一；`--auto` 可显式启用关键词自动路由。**硬性约定：同一篇文章的封面与正文图必须同一 `--style`**，建议把该篇随机到的 slug 记入 frontmatter `style` 字段，正文卡沿用同一 slug；figures 正文卡通过 `{{PALETTE_*}}` 自动继承该风格配色，保证一篇文章内风格一致。

32 套风格已全部内置为模板（[scripts/cover-generator/templates/](scripts/cover-generator/templates/)，清单见 manifest.json），skill 自包含、无外部依赖，离线可用。

## 发布（可选）

如需转 HTML 或发布到微信公众号，按「第六步：转 HTML」和「第七步：发布到微信公众号」执行，规范见 [references/publishing.md](references/publishing.md)。

## 文件说明

| 文件 | 用途 | 何时读 |
| --- | --- | --- |
| [references/planning.md](references/planning.md) | 规划文档规范与检查清单 | 第二步规划系列时 |
| [references/article.md](references/article.md) | 单篇写作规范与检查清单 | 第四步写每篇时 |
| [references/images.md](references/images.md) | 配图方案（模板化配图/Sharp/Mermaid/实拍 + 存放与锚点规范） | 需要配图时 |
| [references/publishing.md](references/publishing.md) | 公众号发布适配 | 需要发布时 |
| [config.yaml.example](config.yaml.example) / [config.yaml](config.yaml) | 发布配置（公众号凭据、缺图策略；转 HTML 参数走命令行）。example 是模板，复制为 config.yaml 后填写凭据；config.yaml 不入库 | 首次发布前复制并填写 |
| [scripts/md-to-html.py](scripts/md-to-html.py) | md → 微信兼容 HTML（主题指定/随机、mermaid 处理） | 每篇写完转 HTML 时 |
| [scripts/publish-wechat.py](scripts/publish-wechat.py) | 发布到微信公众号草稿箱（config.yaml 驱动，支持 --dry-run） | 需要发布时 |
| [scripts/update-wechat-draft.py](scripts/update-wechat-draft.py) | 更新/修复已发布草稿（按记录定位、复用图片 URL、UTF-8 发送） | 需要更新草稿时 |
| [draft-records.example.json](draft-records.example.json) / [draft-records.json](draft-records.json) | 草稿记录（media_id、标题、摘要、封面、图片映射、相对 base_dir 的文章路径），发布后自动写入；同标题重复发布会被拦截。example 是空模板；真实记录含本机路径，不入库（.gitignore），由脚本自动创建 | 更新草稿时 |
| [assets/templates/](assets/templates/) | 三个可直接复制的模板 | 建规划、素材库、写文章时 |
| [scripts/cover-generator/](scripts/cover-generator/) | 封面生成脚本、HTML 模板与 Templater 示例 | 需要批量生成封面时 |
| [scripts/check-images.mjs](scripts/check-images.mjs) | 配图一一对应核对脚本（断链/未用图/缺封面/缺正文图） | 发布前核对配图时 |
| [scripts/check-articles.mjs](scripts/check-articles.mjs) | 内容厚度核对脚本（正文 3500-8000 字） | 发布前核对内容厚度时 |

