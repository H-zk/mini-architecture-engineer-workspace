---
name: external-article-analysis
description: 外部文章分析执行流，无需特定措辞——操作者给出文章链接（一篇/一组，微信/博客/官方文章等网页正文）并要求分析（「分析一下这篇文章」「结合工作区看看」「辩证分析」「有什么可沉淀的」等任何说法）即加载：网页读取工具全量直读 + 读后定性 → 逐篇骨架提炼对照本区（覆盖/同构/真空隙/撞车）→ 三层结论 + 裁决点，仅分析不自动落实。对象判据 = 输入形态：文章无仓可锚、无引入判定——skill 仓库分析走姊妹 skill skill-fit-eval，判据层引用其 Gates 与 exps skill-ecosystem-fit 不复写；混合输入（文章+仓库）分治合并。
updated-at: 2026-08-30
triggers:
  - 分析这篇文章
  - 这几篇文章有什么可沉淀
  - 结合工作区辩证分析这篇文章
  - 文章方法论分析
---

# external-article-analysis

> 本文是「外部文章分析 → 对照沉淀建议」执行流的单一真源。**分工**：本文管取数 / 轮次 / 产物；评估判据（三层结论 / 正交 / 不翻案 / 阴性产出）真源 = [`skill-fit-eval`](../skill-fit-eval/SKILL.md) Gates 与内部经验库 `exps/workflow/skill-ecosystem-fit-portrait-first.md`（经验条目不随产物分发，随使用重建），本文只引用不复写。任务属 `#workspace-optimize`（自定义输入立项；Lifecycle / reopen / review 门禁随 workspace-ops，本文不复制协议骨架）。
> **无独立状态机**：本 skill 由 `#workspace-optimize` 任务承载（两态 Lifecycle 见 workspace-ops），本文件 frontmatter 不设 `states:`。

## When（何时触发）

- **自然触发（无需任何特定措辞）**：操作者给出**文章**链接（一篇 / 一组——微信、博客、官方文章等网页正文）+ 分析意图——「分析一下」「结合工作区现状看看」「辩证分析」「有什么可沉淀 / 可借鉴」等任何措辞均命中本流程。
- **对象判据 = 输入形态**：文章无仓可锚、无「引入与否」判定；链接是 git 仓库 → [`skill-fit-eval`](../skill-fit-eval/SKILL.md)（姊妹 skill，四轮 + 引入判定）。
- **混合输入（文章 + 仓库）分治**：文章部分走本文、仓库部分走 skill-fit-eval，各出产物后综合层合并。
- **不触发**（就近路由）：广域「找些 skill 提效」→ 先画像后找调研（exps skill-ecosystem-fit）；同事库 / 开源工作区整体对比 → colleague-kb-synthesis；已 vendor 安装 skill 的安全确认 → VENDOR.md。
- **立项归属**：`#workspace-optimize` 自定义输入；裸链接 + 分析指令而无标签时，按 WORKFLOW §1.3 模糊地带反问一句确认立项——问的是「立不立」，不是「换措辞再说一遍」。

## Steps（两轮 + 裁决）

| 轮 | 载体 | 动作 | 产出 |
| ---- | ---- | ---- | ---- |
| ① 立项锚定 | 主会话 | 立项 + 网页读取工具全量直读 + 读后定性 | 任务目录 + 文章清单表 |
| ② 分析 | 主会话（深读轮可 subAgent） | 逐篇骨架提炼 → 对照本区 → 三层结论；点名变体按需 | `report.md` |
| ③ 裁决 | 操作者 | 裁决点清单 → 裁决 → 落实 → 收尾 | 裁决闭环记录 |

### ① 立项锚定轮

- 在 `workspace-optimize/` 立项（`task-<日期>-<主题>`），README 声明复用本文 + 判据真源，不重造方法论。
- **锚点 = 链接本身**（文章无 commit 可锚）；操作者给出链接并指示分析 = 授权只读取数。
- **取数**：网页读取工具全量直读（会话可用的 webReader / WebFetch 类工具，择一），分析以原文为锚、不拿转述版单独成析；**文章清单表**登记链接 + 主题 + **读后定性**（原文 / 忠实摘要 / 有损摘要 / 营销向）——多篇互为译本时以原文为主锚（拿摘要当原文会误导分析：压缩有损耗、译注混入解读者立场）。

### ② 分析轮

- **逐篇三段**（报告骨架见 [references/report-skeleton.md](./references/report-skeleton.md)，产 report.md 前必读）：
  1. **方法论骨架**：引原文关键句留痕，不转述失真；
  2. **对照本区**：逐条映射 已覆盖 / 已覆盖·更细 / 同构 / 真空隙 / 撞车 / 不适配（点名本区对应机制 / skill / BACKLOG 行）；
  3. **三层结论**：✅ 即用 / 🟡 固化候选 / 参照（判据见 skill-fit-eval Gates，即用不埋裁决）。
- **综合层**（多篇时）：跨篇交叉对照——同族印证 / 互补 / 冲突，共同指向的真空隙；单篇可省。
- **点名变体**（操作者点名才启动，非默认步骤——文章分析保持轻量，不照搬 skill-fit-eval 四轮）：
  - **辩证版**：正题（印证清单）→ 反题（盲区与不适配，要有具体论据不止态度）→ 合题（真空隙与建议）；
  - **深读轮**：叙事者利益分析（把销售动机从规律里拆出来，多源收敛处 = 高置信规律）+ 跨源定律核对；
  - **show-me 可视化**：经指示产 HTML，随任务目录留档。

### ③ 裁决轮

- 裁决点清单呈报 → 操作者裁决 → 落实（exps 增补行 / BACKLOG 素材行 / 即用品生效 / 移交回顾）→ 收尾走 workspace-ops 门禁。
- 裁决未出的点留任务 CURRENT「回顾时裁决」节，不挂起任务（「待对账」钩子同款语义）。

## Gates（评估纪律——真源 = [`skill-fit-eval`](../skill-fit-eval/SKILL.md) Gates）

- **同源沿用、不复制正文**：仅分析不自动落实 / 已裁决不翻案（新证据冲突显式立「翻案申请」段）/ 三层结论不混层（✅ 即用不埋进待裁决框架）/ 阴性结论也是产出——判据定义与完整措辞见真源；本文与报告均只引判据名 + 出处（exps skill-ecosystem-fit），不维护第二份真源。
- **本文差异项——不动 position 基准**：对比材料不改基准，印证仅留档。

## Outputs

- `report.md`（必产物）：结论先行 + 逐篇（骨架 / 对照 / 三层）+ 综合层（多篇时）+ 裁决点清单 + 修订记录；骨架见 [references/report-skeleton.md](./references/report-skeleton.md)。
- 多主题变体：每主题分报 `report-<name>.md` + 综合层 `report.md`；辩证 / 深读产物按点名产出（`report-deep-synthesis.md` 等）。
- **无代码交付、无 temp 克隆**（区别于 skill-fit-eval——文章取数只读网页，不落仓库副本）。
- 沉淀惯例（裁决轮落实，不自动写）：新判据 / 判例 → exps skill-ecosystem-fit 增补一行（合并优先）；INDEX 登记摘要。

## Verify（DoD）

- report.md 结论先行；每篇观点可溯（链接 + 读后定性 + 原文关键句）；三层结论齐且即用品无混层；骨架符合 references/report-skeleton.md。
- `python .tools/workspace-check.py --task <当前任务>` errors=0。
- 首用回写：本 skill 首个真实分析任务收尾时，回写使用偏差进该任务 README（首用验证范式，见 exps skill-authoring-review——经验条目不随产物分发，随使用重建）。
