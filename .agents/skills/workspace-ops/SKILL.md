---
name: workspace-ops
description: 工作区迭代优化（#workspace-optimize / #工作区优化）任务总入口与生命周期单一真源：定期维护菜单（内置 4 项 + 扩展位 1 项）与两步交互、按内容路由到对应 skill（审视工作流 / 阶段回顾 / 学习外部工作区 / 知识库加固）、两态状态机与 reopen 协议、产物约定。立项后先读本 skill 再路由；业务工作不走本标签。
updated-at: 2026-08-17
triggers:
  - "#workspace-optimize"
  - "#工作区优化"
  - 工作区迭代优化
states: [进行中, 已完成]
---

# workspace-ops

> 本文是 `#workspace-optimize`（工作区迭代优化）任务的**总入口 skill**：承载本标签执行约定（维护菜单、两步交互、路由表、产物约定）与 Lifecycle（状态机 + reopen 协议），是单一真源；WORKFLOW §1.3 只保留路由句。
> 术语：**工作区 ⊃ 工作流**——本标签是**工作区自身迭代优化总入口**（核心子域 = 工作流层：标签状态、执行流 skill、门禁；运营子域 = 维护类、知识库类、对比类、回顾类工作）。

## When（何时触发）

- 消息开头标签 `#workspace-optimize` / `#工作区优化` **立项后**，按内容路由到对应 skill 执行（见路由表）。
- 单字词启动器 `workspace-optimize` / `工作区优化`（消息仅为该词，无 `#`、无后续内容）→ 弹维护菜单（**不立项**），见下方「维护菜单与两步交互」。
- **边界**：业务工作（你们产品的功能 / 线上问题）一律走 `#feat`/`#case`/`#tech`/`#research`，不进本标签。

## Lifecycle（状态机 + reopen 协议）

- **状态集**：`{进行中, 已完成}` 两态（frontmatter `states:` 即机器校验登记处，`workspace-check.py` 从该处读取）。
- **路径**：`进行中 → 已完成`（收尾）；等裁决 = `next` 承载、等外部 = `blocker` 承载（无「阻塞」态，机制见 [WORKFLOW §2.6](../../../WORKFLOW.md) 状态机不变量）。
- **reopen 回边 `已完成 → 进行中`**（本标签特有：治理任务多轮增评是设计内行为）：
  - **判据**：同任务还有活没干完 = reopen；不同主题 / 新机制想法 = 新任务或 BACKLOG。
  - **协议** = [WORKFLOW §2.6](../../../WORKFLOW.md) 通用 reopen 协议（活跃区硬截止 / 翻回留痕收场 / 新会话增补 / `sprint-version` 不变）；本标签特有：`review:` 留痕按轮次追加。
- **门禁分层**：
  - 本标签特有（本 skill 自持）：README/CURRENT 齐备 + `review: passed` 完成确认留痕（操作者确认后写，完成判定权见 WORKFLOW §2.6 完成前闸门）。
  - 跨类型基线（见 WORKFLOW §2.6/§7）：完成前闸门 + §7 收尾清单 + 沉淀询问 + workspace-check `errors=0` 事前门禁 + 留痕。

## 维护菜单与两步交互（单字词启动器规范）

`workspace-optimize` 单字词 → 第一步呈现菜单（内置项 + 扩展位）+ 自定义输入；**选中内置维护项后**第二步按项弹**专属辅助说明**输入（必填项留空会重问；自定义输入直接立项、不进第二步；扩展位选中后提示接入思路、也可直接转入自定义描述立项）：

| 维护项 | 状态 | 第二步追问 | 必填 |
| ------ | ---- | --------- | ---- |
| 审视工作流 | **内置** | 聚焦（如「BACKLOG 消化」「某 skill 压测」；留空=全面） | 否 |
| 阶段回顾 | **内置** | 重点/锚点（留空=按 `retrospectives/README.md` 自动） | 否 |
| 学习外部工作区 | **内置** | 学习对象本地路径（= 只读授权；同事库/开源参照先按 `position/` 登记）+ 聚焦维度（留空=全面）；流程见 [colleague-kb-synthesis](../colleague-kb-synthesis/SKILL.md) | 是（对象路径） |
| 知识库加固 | **内置** | 已结 CASE/需求素材 + 结论查询入口（地址/系统）；流程见 [notes-reinforcement](../notes-reinforcement/SKILL.md) | 是（素材+入口） |
| 维护仓库 | 扩展位 | 提示：模板未内置执行 skill，接入思路见 [GUIDE](../../../GUIDE.md) §3；也可自定义描述直接立项 | - |

## 路由表（立项后按内容路由，不写独立执行节）

| 操作类型 | 路由 skill |
| -------- | ---------- |
| 工作流瘦身 / 压测 / 治理审计 | `workspace-grill` |
| 阶段回顾（执行质量复盘，非 skill 流程） | 方法见 [`retrospectives/README.md`](../../../retrospectives/README.md) |
| 学习外部工作区（同事库/开源参照对比） | [`colleague-kb-synthesis`](../colleague-kb-synthesis/SKILL.md) |
| 知识库加固（已结 CASE/需求反哺 notes） | [`notes-reinforcement`](../notes-reinforcement/SKILL.md) |
| 维护仓库 | **未内置**（扩展位）——按 GUIDE §3 自建后登记进本表 |

## 维护节奏与依赖

- **随意触发**：审视工作流（workspace-grill）——操作者按需发起，每迭代 ≥1 次（唯一 BACKLOG 评估者）。
- **硬锚点 = 迭代末**：阶段回顾（独占归档批次 / 定下迭代 sprint-version + 周期 / exps 毕业清单确认 / 待对账打捞）。
- 软链：colleague-kb-synthesis 跑完建议接一次 workspace-grill（skill 内已内置该提示）。
- 硬依赖：新迭代任务立项依赖回顾定 `sprint-version`（回顾没跑、旧迭代任务留活跃区 = 设计内行为）。

## Outputs（产物约定）

产物按性质落（`reference/` / `exps/` / `HUMAN.md` / `notes/`），任务目录承载过程（`README.md` + `CURRENT.md`）；收尾走 WORKFLOW §7 + §2.4 沉淀门禁——**这是本标签的核心价值：让操作类工作也走立项 + 收尾门禁，根治漏沉淀**。人类操作类沉淀（操作约定 / 维护事项 / 上手流程）提议写入 `HUMAN.md`、授权后才写。

## Verify（DoD）

- README/CURRENT 齐备，CURRENT 符合 WORKFLOW §2.6 模板（`status` ∈ 本 skill `states:`，纯枚举）。
- `python .tools/workspace-check.py --task <当前任务>` 本标签任务无 error（含 states 读取与 per-status 规则）。
- 涉及真源修改的落地类改动，收尾前跑全量 workspace-check 且 `errors=0`。
