# 配图方案（images）

每篇至少一张示意图或截图；系列封面与章节头图用哪种方式，按下表选。

| 场景 | 方式 | 成本 | 特点 |
| --- | --- | --- | --- |
| 系列封面、每课封面、公众号头图（批量、同篇统一） | 模板化配图（推荐） | 零（无 AI 生图费用） | 同篇风格一致、可控、可批量 |
| 极简封面（纯色 + 文字） | Sharp 合成 | 零 | 更轻量、无浏览器依赖 |
| 正文示意图 | Mermaid（Obsidian 直接渲染） | 零 | 一张图只讲一件事 |
| 操作记录、真实证据 | 实拍截图 | 零 | 必须真实，禁止虚构 |
| 需要手绘感/真实感的正文插图 | AI 生图 | 按量计费 | 用于正文，不用于统一封面 |

## 方案一：模板化配图（推荐，通用 HTML→PNG 引擎）

### 原理

HTML/CSS 模板 + 无头浏览器截图：把标题、副标题、分类、期号等填入模板，渲染成统一风格的 PNG。零生成成本、完全可控，适合「批量出图、同篇一致」的场景——公众号封面、知识库头图、每课封面，以及文章里的知识卡、对比图、示意图等正文配图。同一篇文章内风格必须一致；篇与篇默认随机换风格，指定 `--style` 则全按指定。

### 使用

脚本与模板在 [scripts/cover-generator/](../scripts/cover-generator/)：

- `templates/manifest.json`：模板风格清单（33 项：default + 32 套风格），随机与路由的依据；
- `templates/*.html`：每套风格一个 HTML 模板，占位符统一（`{{SERIES}}/{{LESSON}}/{{TITLE}}/{{TITLE_SIZE}}/{{SUBTITLE}}/{{CATEGORY}}/{{FOOTER}}/{{DATE}}`）；
- `generate.mjs`：Node + Playwright 生成脚本。

```powershell
node generate.mjs --style blueprint --series "XXX 零基础入门" --lesson 05 --title "让机器人动起来" --subtitle "用手柄遥控电机，写第一个控制代码" --category "编程" --out "assets/cover-05.png"
```

参数：`--input <md>` 文章 Markdown 路径（可选，别名 `--md`）：缺省读取 frontmatter 的 `title`/`subtitle`/`lesson`/`category`/`series`/`style` 作默认值，**封面 title 即文章 header 里的 `title`**；命令行显式参数优先（`--title` 等仍可覆盖），frontmatter 有 `style` 时优先用该风格（否则默认随机/`--auto` 路由）、`--style` 模板风格 slug（指定则按指定；不指定默认从 33 套风格里随机选一套）、`--random` 随机选风格（默认行为，可省略）、`--auto` 关键词自动路由（可选，显式传入才启用）、`--template` 直接指定任意 HTML 模板文件（优先级高于 --style，用于文章配图）、`--series` 系列名、`--lesson` 期号、`--title` 标题、`--subtitle` 副标题、`--category` 分类标签、`--tag` 角标标签（对应 `{{TAG}}`，正文卡右上角常用）、`--footer` 底部文字（对应 `{{FOOTER}}`/`{{FOOT}}`，默认「系列名 · 系列教程」）、`--set key=value` 设置任意扩展占位符（可重复）、`--out` 输出路径（默认 cover.png）；`--width`/`--height` 默认 1200×630；`--scale` 默认 2（2 倍高清）。脚本渲染后会自动警告未替换的占位符（如 `{{TAG}}`），出图前留意该警告。

直接传文章生成封面的最简写法（标题等自动取自 frontmatter）：

```powershell
node generate.mjs --input "01-数学竞赛是什么.md" --out "assets/cover-01.png"
```

### 生成文章配图（非封面）

同一引擎可以生成文章中的任意配图：先写一个 HTML 模板（用 `{{key}}` 占位符），再渲染出图。

```powershell
node generate.mjs --template "assets/05/05-知识点卡模板.html" --set 知识点="柯西不等式" --set 说明="两列平方和乘积不小于和的平方" --out "assets/05/05-02-知识点卡.png"
```

规则：

- 正文图模板建议放 `<系列>/assets/NN/` 或 `<系列>/assets/templates/`，与正文图同目录管理；
- 占位符可任意定义，`--set` 一个填一个；没填的占位符会残留 `{{xxx}}`（generate.mjs 渲染后会打印 `[警告]`），出图前留意警告；
- 正文图输出仍遵守「存放位置与锚点一一对应」：输出到 `assets/NN/`、文件名 `NN-序号-用途`、正文引用一一对应；
- 内置正文图模板在 `scripts/cover-generator/templates/figures/`：`card-flow`（流程卡）、`card-list`（列表卡）、`card-compare`（对比卡）、`card-knowledge`（知识点卡），用 `--template` 引用生成，批量复用；系列特有版式可自行新增到该目录。

**正文卡模板占位符清单**（`TITLE`/`TAG`/`FOOT` 已内置：`--title`/`--tag`/`--footer` 直接填；其余为卡内容占位符，必须用 `--set` 逐项填，漏填会残留并触发 `[警告]`）：

| 模板 | 内置 | 必须 --set 的内容占位符 |
| --- | --- | --- |
| card-flow（流程卡） | TITLE / TAG / FOOT | STEP1-STEP4（步骤名）、D1-D4（说明） |
| card-list（列表卡） | TITLE / TAG / FOOT | ITEM1-ITEM9（条目）、S1-S9（副文字） |
| card-compare（对比卡） | TITLE / TAG / FOOT | K1-K8（标签）、V1-V8（值）、D1-D8（说明） |
| card-knowledge（知识点卡） | TITLE / TAG / FOOT | BODY（正文） |

示例（对比卡，注意用 `--tag` 而不是 `--set TAG`）：

```powershell
node generate.mjs --style blueprint --template "...\figures\card-compare.html" --title "四条升学兑现路径" --tag "认知 · 对比" --set K1="保送" --set V1="国集成员（60 人/年）" --set D1="清北等高校，须通过校方考核" ... --set FOOT="系列名 · 认知课" --out "assets/02/02-02-兑现路径.png"
```

> 正文卡模板已做防溢出处理：行高均分（`flex/grid + minmax(0,1fr)`）+ 单元格 `overflow:hidden` + 说明文字 line-clamp 截断。长文本会被裁剪而不是挤出卡片，所以生成后一定要目检一次，确认关键信息没被截掉；如果内容经常被截，就精简文案或换更合适的卡型。

### 模板风格列表与随机/路由

模板清单见 `templates/manifest.json`，共 33 项：`default` + 32 套风格（slug 与 web-image 开源项目的 32 套一一对应）。

按气质分组：

| 分组 | slug |
| --- | --- |
| 印刷传统 | swiss · editorial · newsprint · blueprint · archive |
| 艺术运动 | bauhaus · deco · riso · brutalist · memphis |
| 东方 | wabi · ink · guochao |
| 手作纸感 | sketch · chalk · watercolor · collage · botanical |
| 流行文化 | comic · pixel · y2k · vapor · neon · street |
| 影像商业 | cinematic · retro70 · lineart · glass |
| 数字原生 | terminal · aurora · luxe · product |

**风格选择规则（默认随机）**：

- 用户指定了 `--style`：一律按指定 slug 用对应模板（随机不生效）；
- 未指定 `--style`：默认随机——脚本从 33 套风格里随机选一套（可传 `--random` 显式声明，不传也默认随机）；
- 传了 `--auto`：显式启用关键词自动路由（按 `--title/--subtitle/--category` 关键词选，如「技术/工程/科学」→ blueprint、「数据/政策/升学」→ swiss、「文化/传统」→ ink、「教程/科普/入门」→ sketch），无命中用 default；`--auto` 不与 `--style` 同时用；
- 需要非封面配图：用 `--template` 直接指定模板文件，绕开风格清单；
- 新增风格：在 `templates/` 加 HTML 模板 + 在 manifest.json 登记 slug、名称、适用场景即可接入随机与路由。

**风格一致性（硬性约定）**：随机发生在「篇」粒度——同一篇文章（同一 lesson）的所有图片（封面 + 正文图）必须使用同一个 `--style` slug。流程：封面首次生成时随机定下 slug（或由用户指定），把该 slug 记入文章 frontmatter 的 `style` 字段，正文卡生成时沿用同一 slug；figures 正文卡通过 `{{PALETTE_BG/INK/SUB/ACCENT}}` 自动继承该风格配色，保证一篇文章内视觉统一。

### skill 内其他图片生成环节如何接入

| 环节 | 现有做法 | 与统一引擎的关系 |
| --- | --- | --- |
| 系列/每课封面 | generate.mjs --style（默认随机） | 引擎内置 |
| 正文配图（知识卡、示意卡等） | generate.mjs --template + --set | 引擎内置（见上文） |
| Mermaid 示意图 | Obsidian 直接渲染；公众号发布前转 PNG | 转 PNG 用 Obsidian 插件或 mermaid-cli，不经过引擎；如需统一可后续加 mermaid 渲染脚本 |
| 实拍截图 | 作者真实截图 | 不经过引擎，必须真实 |
| 风格化插图（照片级/手绘） | AI 生图（imagegen skill） | 不经过引擎，按需调用 |
| 32 套风格深度自定义 | 在线参考 web-image 仓库 | 风格已内置为模板；需要更复杂版式时按 web-image 流程另行生成 |

环境要求：Node.js 18+；首次使用先装依赖：

```powershell
npm i -D playwright
npx playwright install chromium
```

没装依赖时脚本会给出同样的提示。

### 与 Obsidian / Templater 集成

在 Obsidian 里用 Templater 加一个 user script，新笔记创建时自动出图：

- 把 [templater-example.md](../scripts/cover-generator/templater-example.md) 里的 `obsidian-cover.js` 放到 Templater 设置指定的 Scripts folder；
- 笔记模板中调用 `<% tp.user.obsidian_cover(tp) %>`；
- 脚本读取当前笔记 frontmatter（title/subtitle/lesson/category/series），调用 generate.mjs 生成 `assets/cover-NN.png`，并把图片路径写回 frontmatter 的 `cover` 字段；
- 如果 Templater 沙箱拦截 `require`，在 Templater 设置里关闭 JavaScript sandboxing（沙箱默认拦截 Node 模块）；
- 脚本里的 generate.mjs 路径写死后，换成实际路径或把脚本复制到 vault 内再改路径。

### 统一风格规则

- **同篇一致、系列多样**：默认每篇随机一套风格（指定 `--style` 则按指定），全系列不强求统一；唯一硬性要求是同一篇文章内封面与正文图完全一致（随机到的 slug 记入 frontmatter `style` 字段复用）；
- 想全系列统一：显式指定同一 `--style` 即可（例如品牌栏目固定用 swiss）；
- 长标题自动缩小字号（脚本按字符数选字号），发布前目检一遍不溢出；
- 公众号封面（头条大图）**必须按 2.35:1 生成**：微信上传建议 1068×455，展示尺寸 900×383；微信会按 2.35:1 从原图中心裁切，比例不符时左右边缘会被裁掉，靠近边缘的文字会被截断。生成命令：

  ```powershell
  node generate.mjs --style blueprint --series "XXX 零基础入门" --lesson 05 --title "让机器人动起来" --subtitle "用手柄遥控电机，写第一个控制代码" --category "编程" --width 1068 --height 455 --out "assets/cover-05.png"
  ```

  文字排版必须落在 2.35:1 安全区内（模板 padding 已留，勿把关键文字贴到左右边缘）。
- 知识库头图/正文示意图常用 1200×630（1.9:1），仅用于 Obsidian 与正文内嵌，**不要直接当作公众号封面上传**；正文卡（figures 模板）默认 1200×630 即可；
- 封面图两种用途尺寸不一致时，优先保证公众号封面 2.35:1，正文引用同一文件即可（正文按宽度自适应显示，不受裁切影响）；
- 输出文件名建议统一 `cover-NN.png`（NN 为期号），便于系列合集引用。

## 方案二：Sharp 合成（轻量备选）

不装浏览器、不依赖 Playwright：Node + sharp 直接在代码里画底色、文字、标签。适合纯色背景 + 少量文字的极简封面；复杂排版（渐变、多行标题、图形）用方案一。取参逻辑可复用 generate.mjs，只替换渲染部分为 sharp API。

## 方案三：Mermaid 与实拍（正文配图）

- 正文示意图：Mermaid 一张图只讲一件事，节点用短词，图紧跟对应文字；Obsidian 直接渲染，公众号发布前转 PNG；
- 操作类文章必须配真实操作截图（界面、运行结果、报错原文），禁止用示意图冒充真实记录；
- 截图注意隐私：用户名、绝对路径、账号密钥、内部资料该裁就裁。

## 存放位置与锚点一一对应

每张图必须有「唯一存放位置 + 正文锚点」，双向可核对：图在文未用、文引图缺失、文件名对不上，都算返工。

### 目录约定

- 系列封面/合集头图：`<系列目录>/assets/cover-NN.png`（NN 为期号，两位，如 cover-05.png）；
- 每课正文图（截图、示意图、Mermaid 转出的 PNG）：`<系列目录>/assets/NN/`（NN 为期号）——**一课一目录，不跨课混放**；
- 文件名：`NN-序号-用途`，如 `05-01-规则手册目录.png`；简短、语义清晰，可混用中英文；
- 未使用/待裁剪的原始素材不直接进 `assets/NN/`，先登记在素材库，确定用到再落盘；
- 封面由 generate.mjs 生成时直接输出到 `assets/cover-NN.png`（脚本已内置该约定）。

### 锚点规则

- 正文引用固定用相对路径：`![说明](assets/NN/05-01-规则手册目录.png)`。**说明文字必须写清图片内容**，禁止用「第 NN 课封面」「配图」这类无信息量的通用标签——封面用「封面：本课主题」格式，正文图用「图：内容描述」格式，例如 `![封面：奖项与升学——省奖到集训队的四级回报](assets/cover-02.png)`；
- 每课正文只引用本课目录 `assets/NN/` 的图；跨课引用只允许封面（合集页引用各课 `cover-NN.png`）；
- 封面在笔记 frontmatter 用 `cover: assets/cover-NN.png` 字段登记，正文开篇的图片引用与它保持一致；
- Mermaid 图直接写在正文（Obsidian 内无需文件）；发布前转出的 PNG 必须命名归档到本课目录并在正文替换为图片引用，原 Mermaid 代码删除或保留二选一，不能两者并存造成混淆；
- 图片路径在正文、frontmatter、素材库三处出现的写法完全一致，不混用 `assets/NN/xxx.png` 与 `assets/xxx.png` 等变体。

### 一一对应核对（发布前必做）

1. **正向**：正文里每个 `![...](...)` 的路径都能找到对应文件（无断链）；
2. **反向**：`assets/NN/` 里每个文件至少被正文引用一次，未引用的删除或移出正文目录；
3. **改名即全改**：文件名/路径改动必须同步更新正文引用、frontmatter cover、素材库登记——全系列搜索旧名替换；
4. **登记表**：素材库「截图与照片」表登记每张图的 文件 ↔ 用途 ↔ 正文引用位置，作为唯一核对源；
5. **自动化核对**：在系列目录运行 `node <skill 路径>/scripts/check-images.mjs --root .`，脚本自动扫全部正文引用（含 `![]()`、`![[...]]` 嵌入、frontmatter cover）与 assets/ 图片文件，输出断链与未用图清单；0 问题才算通过（用法见脚本头部注释）。

## 配图检查清单

- [ ] 同篇封面与正文图风格一致（默认每篇随机，指定 --style 则按指定；slug 已记入 frontmatter style 字段）
- [ ] 图片存放符合目录约定（封面 `assets/cover-NN.png`、正文图 `assets/NN/` 一课一目录）
- [ ] 正文引用路径与文件一一对应：无断链、无未用图
- [ ] 文件名改动已同步正文、frontmatter、素材库
- [ ] 已运行 check-images.mjs，0 断链、0 未用图
- [ ] 标题不溢出、无乱码（模板已带中文字体栈）
- [ ] 导出尺寸符合用途：公众号封面 2.35:1（1068×455 或 900×383），知识库头图 1200×630，正文卡按需
- [ ] 发布前确认封面比例：publish-wechat.py 会检查封面宽高比，偏离 2.35:1 会警告/中止
- [ ] 截图无隐私信息
- [ ] 生成脚本环境（Node/Playwright）已就绪；未装时给出了安装说明

## 可参考的开源项目（GitHub）

不想从零写模板时，以下热门仓库可直接参考或使用（使用前确认各自许可证）。**这些仓库仅作在线参考，不随 skill 附带，需要时直接访问对应 GitHub 仓库**：

| 仓库 | 亮点 | 适合场景 |
| --- | --- | --- |
| [Lruihao/CoverView](https://github.com/Lruihao/CoverView) | 博客封面生成器：7 种主题、100+ 图标、15+ 背景图案、平台尺寸预设，PNG/JPEG/SVG 导出 | 想先在线调模板、找风格灵感；适合博客/公众号封面 |
| [soumendrak/Advanced-CoverView](https://github.com/soumendrak/Advanced-CoverView) | CoverView 增强版：`npx coverview-skill` 一条命令装 agent skill（支持 Codex/Claude），另有 Satori 渲染的 HTTP API，支持 7 布局、18 背景图案、13 平台尺寸 | 想直接用现成 agent skill 出封面，或程序化调用 API |
| [whyubel1eve/web-image-skill](https://github.com/whyubel1eve/web-image-skill) | HTML/CSS 渲染图片的 skill（MIT）：32 套预设风格、20+ 尺寸预设、两条导出通道（零依赖 SVG foreignObject 导出 + Chrome headless 截图），附中文排版与构图参考 | 需要风格化封面/卡片/海报，或想借鉴其零依赖导出引擎 |
| [gracile-web/og-images-generator](https://github.com/gracile-web/og-images-generator) | 纯 HTML/CSS 模板生成 OG 图，无需无头浏览器（HTML→SVG→PNG） | 想要更轻量、无浏览器依赖的生成链路 |
| [svycal/og-image](https://github.com/svycal/og-image) | SavvyCal 的开源 OG 图服务，自定义 HTML/CSS 模板 | 参考服务化 OG 图架构 |

**关于开源仓库**：上述仓库已不再随 skill 附带（skill 已自包含）。需要参考源码或最新版时，直接访问对应 GitHub 仓库；web-image 的设计方法论（styles.md / design.md / scenes.md / formats.md）可在线阅读或浅克隆到需要的位置。

**选型建议**：

- 想「直接用别人的」：优先 `npx coverview-skill`（Advanced-CoverView）或 CoverView 在线编辑器，出图后存进 assets 即可；
- 想「自己 skill 内置」：保留本 skill 自带的 [generate.mjs](../scripts/cover-generator/generate.mjs)（Playwright）作为确定性基线；无浏览器环境可借鉴 og-images-generator 的 HTML→SVG→PNG 思路或 web-image-skill 的页内导出引擎；
- 想「完全无浏览器」：参考 [@vercel/og](https://vercel.com/docs/concepts/functions/edge-functions/og-image-generation) / [Satori](https://github.com/vercel/satori) 路线（Advanced-CoverView 的 API 即基于 Satori）；
- 风格灵感：web-image-skill 的 32 套风格（瑞士国际主义、包豪斯、国潮、蒸汽波等）可直接描述给 AI 作为模板风格参照。

