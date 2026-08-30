---
name: tech-consult
description: 技术咨询（#tech / #咨询）任务执行流：澄清问题 → 知识库分层查证（notes/reference/exps 优先，涉及「系统当前如何运行」回 src/ 代码核实）→ answer.md 结论先行。无代码交付，两态 Lifecycle（进行中 → 已完成，单步直达不设 reopen）。
updated-at: 2026-08-29
triggers:
  - "#tech"
  - "#咨询"
  - 技术咨询
states: [进行中, 已完成]
---

# tech-consult

> 本文是技术咨询流（`tech/`：目录产物 / 执行步骤 / DoD / Lifecycle）的单一真源。通用生命周期（立项 / CURRENT 骨架 / 收尾清单）见 [WORKFLOW §2、§7](../../../WORKFLOW.md)。

## When（何时触发）

- 消息开头标签 `#tech` / `#咨询`，且需写交付物/留档——门槛：能即时从已有知识答出的当场答（不打标签），仅当结论可复用且 `notes/` 尚无时，提议沉淀到 `notes/`。
- 典型场景：被问「某技术方案怎么选 / 能不能这样做 / 容量怎么估」。

## Lifecycle（状态机）

- **状态集**：`{进行中, 已完成}` 两态（frontmatter `states:` 即 `workspace-check.py` 的机器校验登记处）；「等提问方反馈」→ `next`、「等外部信息」→ `blocker`（无「阻塞」态，机制见 [WORKFLOW §2.6](../../../WORKFLOW.md) 状态机不变量）。
- **路径**：`进行中 → 已完成` 单步直达，无中间节点；tech 一次性、**不设 reopen**（完成后新问题新开任务）。
- **门禁分层**：
  - **tech 特有（本 skill 自持）**：`answer.md` 存在且 DoD 三条满足（结论明确可直接采纳 / 依据可追溯 / 风险与前提假设已标注）。
  - **跨类型基线（见 WORKFLOW §2.6/§7）**：完成前闸门（操作者确认制）+ §7 收尾清单 + 沉淀询问时机 + workspace-check `--task <当前任务>` `errors=0` 事前门禁 + 留痕。
- **review 事件**：tech 无独立 review 环节（跨标签机制见 [WORKFLOW §2.6](../../../WORKFLOW.md) 状态机通用协议）；操作者完成确认留痕记 CURRENT 历史正文一句。
- 架构能力反思（一句触发点）：触发点 = 收尾（→ `已完成`）——规则与各标签触发点单一真源 = [ARCHITECTURE.md](../../../ARCHITECTURE.md) §5 触发点表（阻断）。

## Steps

1. **澄清问题** → 确认真实意图、约束条件（成本、周期、存量兼容），写 `README.md`。
2. **查证（知识库优先，分层回退）** → 先查 `notes/`、`reference/`、`exps/` 既有结论；**命中且足够 → 直接答**；不够或涉及「系统当前如何运行」→ 回 `src/` 代码核实（代码 = 地面真相，可靠性分层与冲突仲裁见 WORKFLOW §5.1）。
3. **给结论** → `answer.md` 结论先行，附依据、风险、备选；给量化数据而非「差不多」。
4. **收尾** → tech 无代码交付，走 `进行中 → 已完成`（Lifecycle 见上，操作者完成确认留痕记 CURRENT 历史正文一句）；结论可复用 → 沉淀到 `exps/` 或补 `notes/`（收尾门禁见 WORKFLOW §7）。

## Outputs（目录产物）

```text
tech/tech-YYYY-MM-DD-xxx/
├── README.md       # 问题、背景、约束、提问方（静态）
├── CURRENT.md      # 活状态（WORKFLOW §2.6 模板）
└── answer.md       # 结论先行 + 依据 + 风险 + 备选方案
```

## Verify（DoD）

- [ ] 结论明确、可直接采纳；
- [ ] 依据可追溯（引用了哪份文档/数据）；
- [ ] 已标注风险与前提假设。
