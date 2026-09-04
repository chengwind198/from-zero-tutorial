# 转 HTML 与公众号发布（publishing）

系列文章在 Obsidian 里写完后，按「第六步：转 HTML → 第七步：发布微信（可选）」走。本文是这两步的规范。

文章默认位于 `<项目根>/generated/<英文标题>/`（SKILL.md「输出目录约定」）；下文命令示例里的路径按实际位置替换，命令默认在技能根目录执行。

## 一、转 HTML（每篇必做）

### 命令

以下命令默认在**技能根目录（SKILL.md 所在文件夹）**执行，`--input` 传你自己的文章路径；换机器只需先 `cd` 到该技能目录，命令无需改动。

```powershell
# 先干跑：看会用什么主题、输出到哪
python scripts/md-to-html.py --input "<项目根>/generated/<英文标题>/01-数学竞赛是什么.md" --dry-run

# 正式转换（未指定主题 → 随机）
python scripts/md-to-html.py --input "<项目根>/generated/<英文标题>/01-数学竞赛是什么.md"

# 指定主题（可选参数：--html-dir 输出目录，--mermaid-cmd 渲染命令）
python scripts/md-to-html.py --input "<项目根>/generated/<英文标题>/01-数学竞赛是什么.md" --theme refined-blue --mermaid-cmd mmdc
```

### 主题选择规则

- `--theme <slug>` 指定 → 用指定主题（themes/*.json，共 15 套）；
- 未指定 → 从 themes/ 随机选一套。

主题只影响 HTML 排版（正文样式），与配图风格（generate.mjs 的 `--style`）是两个独立系统，不要混用。
md → HTML 的全部参数（`--theme` / `--html-dir` / `--mermaid-cmd`）都走命令行，config.yaml 只配置公众号发布。

### Mermaid 处理

微信公众号不支持 Mermaid，发布前必须渲染成 PNG：

- 传 `--mermaid-cmd mmdc`（默认就是 mmdc）后，脚本自动把 ```mermaid 块渲染成 `mermaid-NN.png`（输出在 HTML 同目录）并替换为 `<img>`；
- 未配置时：普通转 HTML 会保留源码占位并打印 `[警告]`；`--for-publish`（发布脚本内部启用）会直接中止，防止缺图发布。

### 图片与封面

- 正文图：保持 Markdown 里的相对路径（如 `assets/02/02-01-奖项通道.png`），HTML 输出在文章同目录时路径依然有效；发布时由发布脚本上传替换为微信 URL；
- 封面：取 frontmatter `cover`，发布脚本上传为微信封面素材；转 HTML 本身不移动封面。

### 输出与检查

- 默认输出与 Markdown 同目录：`<文章目录>/<文章名>.html`（HTML 里图片仍是相对 Markdown 的 `assets/...`，同目录打开即不破图；需要子目录时用 `--html-dir html`，发布/更新草稿流程会显式使用 html/ 子目录）；
- 转换器为 skill 内置实现（markdown + BeautifulSoup 套主题内联样式），支持主题全套样式、高亮标记（`==`/`++`/`%%`/`&&`/`!!`/`@@`/`^^`）、列表序号/项目符号、表格、分节符；不依赖 weflow 等外部项目；
- 转完检查：HTML 无 `{{...}}` 残留、无断图、正文图与封面引用完整。

## 二、发布到微信公众号（可选）

### 首次配置 config.yaml

首次使用先把模板复制为配置文件再填写（config.yaml 已被 .gitignore 忽略，凭据不入版本库）：

```powershell
Copy-Item config.yaml.example config.yaml
```

然后编辑 skill 根目录 [config.yaml](../config.yaml)，填入：

```yaml
default: main
accounts:
  main:
    name: 你的公众号名称
    app_id: 你的AppID
    app_secret: 你的AppSecret
    author: 你的署名
publish:
  allow_missing_images: false
```

### 命令

```powershell
# 干跑：不调微信 API，核对账号/标题/图片清单
python scripts/publish-wechat.py --input "<项目根>/generated/<英文标题>/01-数学竞赛是什么.md" --dry-run

# 正式发布到草稿箱
python scripts/publish-wechat.py --input "<项目根>/generated/<英文标题>/01-数学竞赛是什么.md"
```

可选参数：`--theme`（HTML 主题，缺省随机）、`--html-dir` / `--mermaid-cmd`（透传给 md→HTML）、`--title` / `--digest`（覆盖提取值）、`--cover`（封面，优先级最高）、`--account`（多账号）、`--allow-missing-images`（覆盖 config）。

### 发布流程（实现参考 weflow 的 publish.py / api.py，运行不依赖 weflow）

1. 读取 config.yaml，校验 AppID/AppSecret；
2. 用 md-to-html 生成 HTML（发布模式，mermaid 未渲染即中止）；
3. 上传正文图片：`/media/uploadimg`（返回永久 URL、不占永久素材配额）→ 替换 HTML 里的 `src`；
4. 上传封面：`/material/add_material?type=thumb`（占用永久素材额度）→ `thumb_media_id`；封面优先级 `--cover` > frontmatter `cover` > 文章第一张图；
5. 创建草稿：`/draft/add`，返回 `media_id`。

### 注意事项

- **凭据安全**：config.yaml 含密钥，已在 .gitignore 中、不要提交到仓库（模板见 config.yaml.example）；发布脚本不打印密钥；
- **正文图用 uploadimg、封面用永久素材**：封面每月有配额，重复发同一封面会重复占额度；
- **缺图守卫**：引用了但上传失败的图片默认中止发布，避免产出缺图草稿；
- **中文编码（重要）**：微信 API 会把请求体里的 `\uXXXX` JSON 转义当字面文本存储。发布/更新脚本一律用 `ensure_ascii=False` 以 UTF-8 中文原文发送，不要改用 `json=` 裸参数（requests 默认 `ensure_ascii=True`，会造成草稿箱全乱码）；
- **表格手机判据**：375px、14px 下无横向滚动，列 ≤3，表头 ≤6 字，URL/长命令不放表格；
- **隐私红线**：截图裁掉用户名、绝对路径、密钥；真实人物/机构先确认授权；
- **状态与发布信息回写（单一事实源 = 文章 frontmatter）**：
  - 转 HTML 成功后脚本自动把 `status` 追加阶段标记「已生成html」；
  - 发布成功后自动追加「已发布草稿」，并写入 `published_at` / `wechat_media_id` / `wechat_title` / `wechat_digest` / `wechat_images`；
  - 草稿详情（图片 CDN 映射、封面 media_id、文章路径等）另存 `draft-records.json`，供 update-wechat-draft.py 定位/更新草稿；
  - 进度表标记「已发布」，素材库不再重复维护发布表。

## 三、更新/修复已发布草稿（可选）

文章改稿、发现草稿乱码、或要换标题/摘要/封面时，用 `update-wechat-draft.py` 更新草稿，不需要重新发布。

### 定位草稿

```powershell
# 列出全部草稿记录（含发布/更新时间、文章路径）
python scripts/update-wechat-draft.py --list

# 按标题关键词 / 文章路径关键词定位
python scripts/update-wechat-draft.py --key "别急着入坑"

# 直接按 media_id（无记录时自动拉草稿内容并解码 \uXXXX 乱码）
python scripts/update-wechat-draft.py --media-id <media_id>
```

`--key` 匹配到多条记录时会列出全部并要求改用 `--media-id` 精确定位，避免更新错草稿。

### 更新内容

默认重读发布时记录的文章 HTML（`html_path`）；也可显式指定：

```powershell
# 用文章 Markdown 重新生成 HTML（改动正文后）
python scripts/update-wechat-draft.py --key "03" --input "<项目根>/generated/<英文标题>/03-别急着入坑.md" --theme refined-blue

# 直接指定 HTML 文件，并覆盖标题/摘要
python scripts/update-wechat-draft.py --media-id <id> --html "<项目根>/generated/<英文标题>/html/03-别急着入坑.html" --title "新标题" --digest "新摘要"

# 换封面（重新上传为 thumb 素材）
python scripts/update-wechat-draft.py --key "03" --cover assets/cover-03.png
```

### 更新规则

- **图片复用**：正文图优先复用 `draft-records.json` 里已上传的 CDN URL，不重复占上传额度；文章改动后新增的本地图才重新上传；
- **封面复用**：默认沿用草稿原 `thumb_media_id`；只有 `--cover` 指定新封面才重新上传；
- **乱码修复**：无记录且只给 `--media-id` 时，脚本拉取草稿现有内容，把 `\uXXXX` 转义解码为中文后重写——可用来修复历史乱码草稿；
- **编码保证**：更新请求同样以 UTF-8 中文原文发送，更新后脚本会拉取草稿验证标题/摘要/正文无 `\uXXXX`；
- **记录刷新**：更新成功后同步刷新 `draft-records.json`（`updated_at`、标题、图片映射、封面）；
- **记录路径为相对路径**：记录里的 md/html/封面/图片路径都相对该记录的 `base_dir` 存储；换机器或移动目录后，把 `base_dir` 改成新位置即可继续按记录更新；
- **防重复发布**：`publish-wechat.py` 检测到同标题草稿记录时默认中止（提示改用更新脚本），只有显式传 `--duplicate-ok` 才允许另建草稿。

## 发布前检查清单

- [ ] 已转 HTML（第六步），无 `{{...}}` 残留、无断图
- [ ] Mermaid 已渲染成 PNG（或发布中止确认过）
- [ ] config.yaml 已填正确账号，`--dry-run` 通过
- [ ] 标题含主题关键词、副标题有钩子、署名正确
- [ ] 每张表过手机安全判据
- [ ] 封面已指定（--cover / frontmatter cover / 第一张图）
- [ ] 截图无隐私信息，链接逐一打开有效
- [ ] 发布成功后确认 frontmatter 状态与 draft-records.json 已自动回写（素材库不再手动维护发布表）
