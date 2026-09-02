# from-zero-tutorial 单篇模式设计（单 skill 双模式）

- 日期：2026-09-02（v2：补充两模式流程/节点/细节的隔离与复用设计）
- 状态：设计已批准（方案 B：单 skill 双模式；方案 D 三 skill 分层已否决）
- v3：补充单篇图片锚点回填规则
- 关联技能：[from-zero-tutorial](SKILL.md)

## 1. 背景与目标

from-zero-tutorial 当前只支持系列教程（七步流程：规划 → 素材库 → 逐篇写作 → 验证回填 → 转 HTML → 发布）。用户经常只给一个标题要求「写一篇文章」（如公众号文章），却被要求走完整系列流程：建系列规划.md、建素材库.md、回填三处，体验差、成本高。

目标：在同一 skill 内新增「单篇模式」，入口按用户请求自动路由；系列模式行为完全不变；两模式的流程、节点、细节做到**显式隔离（不互相污染）与充分复用（公共资产只维护一份）**。

已确认决策：

1. 字数不放宽：单篇与系列一致，正文 3500–8000 字（check-articles 默认区间）。
2. 配图强制：单篇同样强制封面 + 至少一张正文图（与系列同一标准）。
3. 路由：按用户标题/请求判断单篇还是系列；无法判断时默认单篇。

## 2. 架构与文档物理组织

不改变技能目录结构，只改 SKILL.md、references、templates、check-images.mjs。为了让模式指令**隔离**、公共资产**复用**，文档按三层组织：

| 层 | 位置 | 内容 | 归属 |
| --- | --- | --- | --- |
| 路由与铁律 | SKILL.md 顶部 | 模式信号词、判定规则、模式切换；取材先行/双源核实/写完必验/整篇一次跑完 | 两模式共享 |
| 系列模式 | SKILL.md（原七步章节，原位不动） | 规划.md → 素材库.md → 逐篇 → 验证回填 → HTML → 发布 | 系列专属 |
| 单篇模式 | references/single-mode.md（新增，薄入口只留指向） | 轻量五步全细节（本 spec 第 4 节展开） | 单篇专属 |

- 脚本（md-to-html、publish-wechat、generate、check-*）、33 套封面模板、15 套主题、config/draft-records 机制：两模式共用同一份，**不复制**；
- 写作规范 references/article.md：两模式共享，内部用「模式差异」标注字段与章节的必填性；
- 模板：assets/templates/article-template.md（系列版，现状）保留，新增 assets/templates/article-single-template.md（单篇版）。

### 执行纪律（防串模式）

路由确定后只执行目标模式的节点：

- 命中**单篇模式**：只读 references/single-mode.md + 共享规范（article.md / images.md / publishing.md / scripts）；**禁止执行系列专属节点**（不建系列规划.md、不建素材库.md、frontmatter 不写 lesson、正文不写「下一步」、收尾不回填三处、check-images 用 --strict）；
- 命中**系列模式**：按 SKILL.md 七步执行；**禁止执行单篇专属节点**（不用 --strict、每篇必须 lesson + 「下一步」、回填三处必做）；
- 切换模式（单篇 ↔ 系列）按第 5 节规则补齐/删除对应产物。

## 3. 流程节点隔离与复用矩阵

每个流程节点一行，标注两模式行为与归属（共享 = 同一实现同一规范；隔离 = 各自实现/规范；范围差异 = 同一实现但执行范围不同）：

| 流程节点 | 系列模式 | 单篇模式 | 归属 |
| --- | --- | --- | --- |
| 入口路由 | 按信号词分流 | 同左 | 共享（SKILL.md） |
| 取材 web search | 主题全景 + 学习路径 + 本文补料 | 仅本文主题 | 共享铁律，范围隔离 |
| 双源核实 | 关键数据双源 + 核验日期登记 | 同左 | 共享铁律 |
| 规划 | 建系列规划.md（模板+planning.md） | 对话内给简短大纲，不落盘 | 隔离（单篇无产物） |
| 素材库 | 建素材库.md，按课登记回填 | 在系列目录内 → 并入该系列素材库.md 对应条目；独立单篇 → 不建库 | 隔离（单篇仅在系列目录内并入） |
| 写作字数 | 3500–8000（check-articles 默认） | 3500–8000（同左） | 共享 |
| 写作规范 | article.md：场景开场/术语首现解释/信息块/一稿二改/来源可核实 | 同左 | 共享（article.md） |
| 章节结构 | 基础件 + 按类型可选模块 + 「下一步」必设 | 基础件 + 按类型可选模块；**不设「下一步」**，以延伸阅读收尾 | 共享规范 + 单篇差异 |
| 标题/frontmatter | 「XXX 零基础入门 · NN」+ lesson 必填 | 用户给定标题；frontmatter 无 lesson | 隔离 |
| 封面命名 | 系列资产目录既有约定（如 assets/frc-NN.png / cover-NN.png） | assets/ 下任意清晰文件名 | 隔离（各自约定） |
| 封面生成 | generate.mjs --input <md>，公众号 1068×455（2.35:1），title 取 frontmatter title | 同左 | 共享 |
| 正文配图 | assets/NN/ 一课一目录，至少一张 | assets/ 下即可，至少一张 | 共享引擎，目录规范隔离 |
| 风格一致性 | 封面与正文图同 style，slug 记 frontmatter style | 同左 | 共享 |
| 配图校验 | check-images.mjs（默认：带 lesson 才强制封面/正文图） | check-images.mjs --strict（全部强制） | 共享脚本，参数隔离 |
| 厚度校验 | check-articles.mjs | 同左 | 共享 |
| 转 HTML | md-to-html.py --theme（可指定/随机），无 {{}} 残留 | 同左 | 共享 |
| 发布 | publish-wechat.py --dry-run → 用户确认 → 正式；draft-records.json 防重复 | 同左 | 共享 |
| 标题超长 | 发布拦截 >64 字节，--title 提供短标题，不截断 | 同左 | 共享 |
| 回填 | 三处必做：规划进度表 + 系列合集 + 素材库 | 图片锚点回填：在系列目录内 → 素材库对应条目必回填；独立单篇 → 文章末尾「配图登记」小节（可选） | 隔离 |
| 状态回写 | frontmatter status/wechat_* 由脚本自动追加 | 同左（无 lesson 不影响回写） | 共享 |
| 模式切换 | → 单篇：允许，按单篇收尾 | → 系列：补建规划.md + 素材库.md + lesson + 「下一步」 | 隔离规则 |

## 4. 单篇模式流程（轻量五步）

| 步骤 | 内容 | 与系列模式的差异（隔离点） |
| --- | --- | --- |
| 1 取材 | web search 针对本文主题，关键数据双源核实，来源与核验日期记入「本文素材清单」 | 不摸主题全景；不建素材库.md |
| 2 大纲 | 动笔前在对话中给出简短大纲（不落盘） | 不建系列规划.md |
| 3 写作 | 3500–8000 字；按 article.md 共享规范；标题用用户给定标题 | frontmatter 无 lesson；正文不设「下一步」 |
| 4 配图 | 封面 + 至少一张正文图，同一 style；generate.mjs --input <md> 生成封面 | 无 lesson/期号概念；输出目录 assets/ 即可 |
| 5 验证与收尾 | check-images --strict + check-articles + md-to-html + publish --dry-run；正式发布需用户确认 | 图片锚点回填：位于系列目录内 → 并入该系列素材库对应条目（必做）；独立单篇 → 文章末尾「配图登记」小节（可选）；check-images 加 --strict |

铁律两种模式通用：取材先行、双源核实、写完必验、整篇一次跑完。

### 图片锚点定义与回填

- **图片锚点** = 正文中的图片引用 `![图：内容描述](路径)`，同时携带文件路径、说明文字与所在位置；check-images --strict 保证文件存在、无未用图、有封面与正文图。
- 回填登记内容 = 封面/正文图文件名 + 锚点说明（+ 所在小节），写法与系列素材库 17–20 课的「配图清单列在文末」一致。
- 回填规则：单篇位于已有系列目录内 → 强制并入该系列素材库.md 对应条目；完全独立的单篇 → 「配图登记」小节可选（建议列在文章末尾「参考」之前），不想落盘则写进对话即可。

## 5. 模式路由

触发本技能后，先按用户请求判断模式：

- **系列模式信号词**：系列、从零开始学、零基础入门、第 N 篇、规划、多篇、合集、课程、进阶、续篇；
- **单篇模式信号词**：写一篇、一篇文章、单篇、标题是、公众号文章、只写 XX、独立文章。

判定规则：

- 命中系列信号词（含「规划成系列」「写多篇」）→ 系列模式；
- 未命中系列信号词，但命中单篇信号词 → 单篇模式；
- 两套信号都未命中 → 单篇模式（默认）；
- 两套信号都出现（如「先写一篇，后面做成系列」）→ 系列模式；
- 无法判断时在回复开头说明「已按单篇模式执行，如需系列请说明」。

中途切换：

- **单篇 → 系列**：用户说「继续写下一篇 / 扩成系列」时，补建系列规划.md 与素材库.md，已有单篇转为系列第 1 篇（frontmatter 补 lesson、正文补「下一步」章节），继续系列流程；
- **系列 → 单篇**：允许，按单篇收尾（不强制回填三处）。

## 6. 系列模式

保持现有七步流程与回填规则（规划进度表、系列合集、素材库三处）不变，文档中标注为「系列模式」；「收尾执行约定」（转 HTML + 发布 dry-run 默认执行，正式发布需用户确认）继续适用。

## 7. 文件改动清单

| 文件 | 改动 |
| --- | --- |
| SKILL.md | description 增加单篇触发词；顶部新增「模式路由」+「执行纪律」章节；原七步标为系列模式；新增指向 references/single-mode.md 的单篇入口 |
| references/single-mode.md | **新增**：单篇五步全细节（取材范围、大纲、写作差异、配图、--strict 收尾命令、模式切换） |
| references/article.md | 新增「模式差异」标注：lesson / 标题格式 / 「下一步」章节 系列必填、单篇省略；配图强制两种模式一致 |
| assets/templates/article-template.md | 现状保留（系列版）；补一句「单篇用 article-single-template.md」 |
| assets/templates/article-single-template.md | **新增**：单篇模板（无 lesson、无「下一步」；title/subtitle/tags/created/updated/status/cover/style 保留） |
| scripts/check-images.mjs | 新增 `--strict`：不带时行为不变（仅带 lesson 强制）；带时对所有 .md 强制缺封面/缺正文图 |
| 其余脚本 | 零改动（check-articles 默认 3500–8000 即满足单篇要求） |

## 8. check-images.mjs --strict 设计

- 现有逻辑：缺封面 / 缺正文图检查只作用于带 lesson 的系列文章（frontmatter 含 `lesson:`）。
- 新参数 `--strict`：跳过 lesson 判断，对扫描到的所有 .md 检查缺封面 / 缺正文图。
- 未传 `--strict` 时行为与现在完全一致，系列回归零风险。
- 单篇收尾命令：`node scripts/check-images.mjs --root <文章目录> --strict`

## 9. 单篇模板（frontmatter 示例）

```yaml
---
title: 用户给定标题
subtitle: 一句有钩子的副标题
tags: [主题, 教程]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: [v2 完成]
cover: assets/<文件名>.png
style: <封面生成后回填 slug>
---
```

- 无 `lesson`、无「下一步」章节；
- 发布成功后由 publish-wechat.py 自动追加 status 标记与 wechat_* 字段（现有逻辑，无需改动）。

## 10. 错误处理与边界

- **标题超长**：沿用发布脚本拦截（>64 字节提示用 --title 提供短标题），不截断、不改 frontmatter；
- **无法判断模式**：默认单篇，并在回复开头说明「已按单篇模式执行，如需系列请说明」；
- **无真机/截图素材**：操作类配图允许 figures 模板示意卡 + 官方文档链接，禁止编造截图与数据；
- **路由误判**：用户可随时纠正，按对应模式重新执行（切换规则见第 5 节）；
- **隔离保证**：单篇流程结束时校验未产生系列专属产物（规划.md/素材库.md/lesson/「下一步」）；单篇位于系列目录内时校验素材库对应条目已登记图片锚点；独立单篇无强制产物。系列流程不使用 --strict、不遗漏回填三处。

## 11. 验证方案

1. 单篇端到端：给定一个标题新建测试文章，完整走「取材 → 大纲 → 写作 → 配图 → check-images --strict → check-articles → md-to-html → publish --dry-run」，全程通过；并校验未产生系列专属产物；单篇位于系列目录内时校验素材库对应条目已回填图片锚点；
2. 系列回归：对现有系列目录重跑 check-images（不带 --strict）与 check-articles，结果与改动前一致（历史遗留问题不算新增）；
3. 文档检查：SKILL.md 单篇入口可正确指向 single-mode.md；article.md 模式差异标注与模板一致；
4. 语法检查：`node --check scripts/check-images.mjs`。

## 12. 不在范围内

- 不拆分为多个 skill（方案 D 已否决）；
- 不新增单篇字数档位（决策 1：不放宽）；
- 不新增单篇专属特性（短文模板、反 AI 检测、一键分发等）；
- 不改发布脚本、md-to-html.py、generate.mjs 的行为；
- 不迁移/重排 SKILL.md 现有的系列七步正文（原位标注，降低回归风险）。


## 13. 执行期修订记录（v4）

- 2026-09-02：端到端验证发现原「其余脚本零改动（check-articles 默认 3500–8000 即满足单篇要求）」不成立——check-articles.mjs 默认只扫描 frontmatter 带 lesson 的文章，无 lesson 的单篇会以 0 篇恒通过，字数强制（决策 1）落空。
- 修订：为 scripts/check-articles.mjs 增加 `--strict`（与 check-images --strict 同型：只做开关、不吞参数；带时对所有 .md 强制字数检查，不带时行为不变），单篇模式第 5 步改为 `check-articles.mjs --strict`。
- 受影响文件：scripts/check-articles.mjs（代码）、references/single-mode.md（第 5 步命令与差异速查表）、SKILL.md（执行纪律行）；第 3 节矩阵「厚度校验」行随之由「同左 共享」修正为「共享脚本，参数隔离」。
