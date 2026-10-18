---
name: skill-fit-eval
description: 外部 skill 单仓定向选型评估执行流，无需特定措辞——只要给出 skill 仓库/链接并要求分析（「分析一下这个 skill」「适不适合我们」「能不能直接用」「是否利好现有流程」等任何说法）即加载：锚定基线 → 初判轮简析出 report.md → 深析轮 subAgent 分域（仓内深读/外部口碑/安全组合位）→ 可选实测 → 裁决留操作者；仅分析不自动落实。广域「找些 skill 提效」（无指定对象）不触发——那是先画像后找调研（exps skill-ecosystem-fit-portrait-first）；文章链接输入走姊妹 skill external-article-analysis（判据层共用）。
updated-at: 2026-10-18
triggers:
  - 分析这个 skill
  - 这个 skill 能不能用
  - skill 是否适合本工作区
  - 单仓定向选型评估
  - 按既有案例与规范分析
---

# skill-fit-eval

> 本文是「外部 skill 单仓定向选型评估」执行流的单一真源。**分工**：本文管轮次 / 门禁 / 产物；评估判据的演化史与判例库检索走 [`exps/INDEX.md`](../../../exps/INDEX.md)（条目：skill-ecosystem-fit-portrait-first；模板态空表属预期，条目随使用重建）；vendor 判定与安装后安全确认 = [`VENDOR.md`](../VENDOR.md)。任务属 `#workspace-optimize`（自定义输入立项；Lifecycle / reopen / review 门禁随 workspace-ops，本文不复制协议骨架）。
> **无独立状态机**：本 skill 由 `#workspace-optimize` 任务承载（两态 Lifecycle 见 workspace-ops），本文件 frontmatter 不设 `states:`。

## When（何时触发）

- **自然触发（无需任何特定措辞）**：操作者给出一个（或一组）外部 skill / skill 仓库链接 + 分析意图——「分析一下」「适不适合我们」「能不能直接用」「是否利好现有流程」等任何措辞均命中本流程。
- **立项归属**：`#workspace-optimize` 自定义输入（skill 分析请求本身即自定义输入内容）；裸链接 + 分析指令而无标签时，按 WORKFLOW §1.3 模糊地带反问一句确认立项——问的是「立不立」，不是「换措辞再说一遍」。
- **不触发**（就近路由）：广域「找些 skill 提效」（无指定对象）→ 先画像后找调研（画像四要素见 exps skill-ecosystem-fit-portrait-first）；已 vendor 安装的 skill 安全确认 → VENDOR.md；同事库 / 开源工作区整体对比 → colleague-kb-synthesis；文章输入（链接为网页正文、无仓可锚、无引入判定）→ 姊妹 skill external-article-analysis；**混合输入（文章 + skill 仓）分治**——文章部分走它、仓库部分走本流程，综合层合并。

## Steps（四轮 + 裁决）

| 轮 | 载体 | 动作 | 产出 |
| ---- | ---- | ---- | ---- |
| ① 锚定立项 | 主会话 | 立项 + 锚定基线留痕 + 取数 | 任务目录 + 锚点 |
| ② 初判 | 主会话 | 按 skill 描述与内容**简要分析**，画像对照 + 三关初判 | `report.md` 初版 |
| ③ 深析 | subAgent 分域 | 仓内深读 / 外部使用口碑 / 安全与组合位 | `analysis-<skill>.md` 或 report 深读重写 |
| ④ 实测（可选） | 主会话或 subAgent | 免安装注入 / trial 对比 / 按需召唤 | `trial-<主题>.md` |
| ⑤ 裁决 | 操作者 | 裁决点清单呈报 → 裁决 → 落实 → 收尾 | 裁决闭环记录 |

### ① 锚定立项轮

- 在 `workspace-optimize/` 立项（`task-<日期>-<skill>-eval`），README 声明复用先例（本 skill + VENDOR 安全确认 + exps 判据），不重造方法论。
- **锚定基线留痕**：tag 优先锚 release tag；无 tag 或 tag 滞后锚 `main@<hash>` 并留痕偏差——无锚点的评估结论不可复核。
- **取数与授权边界**：操作者给出链接并指示分析 = 授权只读该仓库；浅克隆进 `temp/`（不落 `.agents/skills/`、不入 vendor lock、收尾清理）。克隆留档进 `src/` **须裁决**，不在初判轮自作主张。外部口碑 / 检索随操作者的分析指示放开（只读），报告留痕来源。

### ② 初判轮（主会话，简要分析）

- 输入 = skill 的**描述与内容**（README + SKILL.md description + 核心文件摘要级阅读）；不追求全仓深读——深读归③，先用最低成本把主判定立起来。
- **画像对照四要素**（先画像后判定，防被候选带着走）：position 硬边界 / 任务高频活动 / 能力底账（`.agents/skills/` INDEX + VENDOR vendor 表 + `.tools` + MCP，防重复引入）/ BACKLOG 痛点与已裁决排除项（防翻案）。
- **三关初判**：
  1. vendor 三信号（路由表引用 / 真实产出调用痕迹 / 标准 SOP 命令，见 VENDOR.md）——引入前全 0 是常态，非否决项、也无翻盘信号；
  2. 适配性——绑定他人工作流假设（特定 issue tracker / TDD / 常驻注入等）直接排除；引擎形态判据（常驻注入 vs 渐进披露、目标平台打包是否含本引擎、器官型依赖 INDEX/BACKLOG/红线上下文）；
  3. 已有替代——Agent 原生或自研机制覆盖即不引入；同族候选画**覆盖拼图**防「引入 A 即可替 B」误判。
- 产出 `report.md` 初版（**产报告前必读** [references/report-skeleton.md](./references/report-skeleton.md)）：三层结论 + 裁决点清单。

### ③ 深析轮（subAgent 分域）

操作者要求「再深入分析」或初判存疑时启动；分域按对象裁剪，常见三路：

| 分域 | 覆盖 |
| ---- | ---- |
| 仓内深读 | 全仓文件（SKILL.md 全文 / hooks / evals / tests / scripts / AGENTS.md）、commit 与 release 史、多副本一致性、评测 harness 定档（证据形态在生态中的位置） |
| 外部使用与口碑 | stars / forks 定位（热度度量传播不度量验证）、issues 全量、外部检索口碑、论文与引述逐条核验存在性 |
| 安全与组合位 | SKILL.md 内容审查（URL / 外发 / 凭证 / 注入模式四查，VENDOR.md）；与既有 skill 的**组合位**评估（相邻组合与单品同等重要） |

- **subAgent 协议**：WORKFLOW §2.6 载体②（prompt 自包含锚清单指针、遇决策点即停）；文件集不相交才并行；主会话独立复核报告含**产物存在性核验**。
- **产物形态二选一**（文首声明分工）：独立深析报告 `analysis-<skill>.md`（report 管适配判定 / analysis 管本体质量与拆件清单）；或 report.md 重写为深读版。

### ④ 实测轮（可选）

- 触发判据：对「规则可执行性 / 产物质量」存疑，或操作者要求——实测后 ❌/✅ 判定更硬。
- 形态：**免安装注入实测**（直读 SKILL.md 路径遵循，不动 `.agents/skills/`）；**trial 改写对比**（用候选规则改写本任务产物供操作者读感裁决）；**工具型按需召唤**（temp 召回配方：浅克隆 + 边界清单 + 用完删）。
- 实测发现回流报告修订：支柱被推翻走**修订留痕**（结论可换支柱存活，不静默改判）。

### ⑤ 裁决轮（操作者）

- 呈报裁决点清单（三层结论 + 实测裁决项）→ 操作者裁决 → 落实（exps 增补 / BACKLOG 素材行 / 克隆留档 / 配方固化）→ 收尾走 workspace-ops 门禁。
- 裁决未出的点留任务 CURRENT「回顾时裁决」节，不挂起任务（「待对账」钩子同款语义）。

## Gates（评估纪律）

- **仅分析不自动落实**：不预装、不登记 vendor 表（未裁决不预装）——评估与引入是两个动作，混在一起会把「值得抄」变成「先装上」。
- **已裁决事项不翻案**：既往单仓评估的排除判定不因新案例重开；新证据正面冲突时在报告显式立「翻案申请」段，不静默改结论。
- **三层结论不得混层**：✅ 即用（零机制 / 零安装 / 零裁决）不得埋进「待裁决」框架——裁决只管「配方是否成文固化」，不管「能不能用」；🟡 固化候选才进裁决；参照（阶段物 / 演进中间态）单列。
- **质量 / 热度 / 适配三轴分开打分**（两两正交）：高质量只提升素材值得抄的档位，不改变引入判定；星数度量传播不度量验证。
- **阴性结论也是产出**：覆盖证明（来源数 × 关键词组 × 方向数）优于硬造推荐。
- **锚点与修订留痕**：一切结论可溯（锚 commit / tag）；支柱推翻走修订记录。

## Outputs

- `report.md`（适配判定，必产物）+ 可选 `analysis-<skill>.md`（独立深析）/ `trial-<主题>.md`（实测）；骨架见 [references/report-skeleton.md](./references/report-skeleton.md)。
- 多对象变体：每对象一份分报 `report-<name>.md` + 综合层 `report.md`（交叉对照 + 综合方案，主报告收敛为摘要 + 指针）。
- 沉淀惯例（裁决轮落实，不自动写）：新判据 / 判例 → 增补 exps skill-ecosystem-fit-portrait-first 一行（合并优先）；克隆留档 → `src/`（经裁决）。
- 无代码交付；temp 浅克隆收尾清理；INDEX 登记摘要。

## Verify（DoD）

- report.md 结论先行、锚点可溯、三层结论齐且即用品无混层；骨架符合 references/report-skeleton.md。
- 深析轮 subAgent 报告经主会话复核（关键论断带原文 / 行号证据，产物存在性核验）。
- `python .tools/workspace-check.py --task <当前任务>` errors=0。
- 首用回写：本 skill 首个真实评估任务收尾时，回写使用偏差进该任务 README（首用验证范式，条目经 [`exps/INDEX.md`](../../../exps/INDEX.md) 检索——经验不随产物分发，随使用重建）。
