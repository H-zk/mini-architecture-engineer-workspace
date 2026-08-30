---
name: research-survey
description: 需求调研（#research / #调研）任务执行流：定边界 → src/ 代码锚定现状（无实现也是结论）→ refs.md 收集 → report.md 方案对比与建议。无代码交付，两态 Lifecycle（进行中 → 已完成 + reopen 回边，多阶段演进是设计内行为）。
updated-at: 2026-08-29
triggers:
  - "#research"
  - "#调研"
  - 需求调研
states: [进行中, 已完成]
---

# research-survey

> 本文是需求调研流（`research/`：目录产物 / 执行步骤 / DoD / Lifecycle）的单一真源。通用生命周期（立项 / CURRENT 骨架 / 收尾清单）见 [WORKFLOW §2、§7](../../../WORKFLOW.md)。

## When（何时触发）

- 消息开头标签 `#research` / `#调研`（进入未知领域，需评估可行性 / 选型 / 预研）。

## Lifecycle（状态机 + reopen 协议）

- **状态集**：`{进行中, 已完成}` 两态（frontmatter `states:` 即 `workspace-check.py` 的机器校验登记处）；「等反馈」→ `next`、「等外部信息」→ `blocker`（无「阻塞」态，机制见 [WORKFLOW §2.6](../../../WORKFLOW.md) 状态机不变量）。
- **路径**：`进行中 → 已完成`（收尾）+ **reopen 回边 `已完成 → 进行中`**（research 特有，tech 不设）——多阶段演进（增项与 reopen）是 research 设计内行为。
- **reopen 协议** = [WORKFLOW §2.6](../../../WORKFLOW.md) 通用 reopen 协议（活跃区硬截止 / 翻回留痕收场 / 新会话增补 / `sprint-version` 不变）；research 特有：增补物 = `report.md` 增补或新阶段文件（多阶段演进的落地形态）。
- **门禁分层**：
  - research 特有（本 skill 自持）：`report.md` 存在且 DoD 满足（方案对比与建议、结论可追溯、「无实现也是结论」、风险与前提标注）。
  - 跨类型基线（见 WORKFLOW §2.6/§7）：完成前闸门（操作者确认制）+ §7 收尾清单 + 沉淀询问时机 + workspace-check `--task <当前任务>` `errors=0` 事前门禁 + 留痕。
  - 架构能力反思（一句触发点）：触发点 = 收尾（→ `已完成`）——规则与各标签触发点单一真源 = [ARCHITECTURE.md](../../../ARCHITECTURE.md) §5 触发点表（阻断；reopen 后增量式只补新信号）。
- **review 事件**：research 无独立 review 环节（跨标签机制见 [WORKFLOW §2.6](../../../WORKFLOW.md) 状态机通用协议）；操作者完成确认留痕记 CURRENT 历史正文一句。
- **沉淀节奏（与 tech 差异）**：tech 收尾一次问；research 每轮增项都可能产出沉淀，收尾时回顾全会话增量问；**每轮收场附轻量方向盲区自查**（只列本轮新暴露的方向盲区——未覆盖的问题域、未验证的假设，供下轮定边界或 BACKLOG 消化）。

## Steps

1. **定边界** → 明确调研要回答的几个关键问题，避免发散，写 `README.md`。
2. **锚定现状（代码优先，地面真相）** → 先回 `src/` 确认相关代码现状（WORKFLOW §5.1）；**无相关实现也是结论**（明确标注「代码已确认无现状」，而非默认没有）；再用 `notes/`、`exps/` 补充背景，外部资料兜底。
3. **收集** → 外部资料汇总到 `refs.md`，标注来源与时效。
4. **对比** → `report.md` 给方案对比表（维度：成本、风险、兼容、周期）。
5. **给建议** → 给推荐项与理由，并给出「验证下一步」。
6. **收尾** → research 无代码交付，走 `进行中 → 已完成`（Lifecycle 见上，操作者完成确认留痕记 CURRENT 历史正文一句）；关键结论沉淀到 `exps/` 或 `notes/`（收尾门禁见 WORKFLOW §7）。

## Outputs（目录产物）

```text
research/research-YYYY-MM-DD-xxx/
├── README.md       # 调研目标、背景、边界、交付对象（静态）
├── CURRENT.md      # 活状态（WORKFLOW §2.6 模板）
├── report.md       # 调研报告：现状、方案对比、推荐、风险、后续计划
└── refs.md         # 引用资料清单（链接 + 摘要 + 可信度）
```

## Verify（DoD）

- [ ] 关键问题逐一有答；
- [ ] 现状已用 `src/` 代码锚定（含「无相关实现」这类结论已标注，而非默认没有）；
- [ ] 结论有可追溯来源；
- [ ] 给出明确的下一步建议。
