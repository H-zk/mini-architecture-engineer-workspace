---
name: workspace-grill
description: 工作区治理审计与决策协议。当用户要求「审视当前工作流」「grill 工作区」「定期 grill 一下」或要压测 WORKFLOW/治理/BACKLOG 时加载。三模式：建议（只读审计，最多 3 项）、决策（一题一决策）、落地（仅执行已确认决策）。
updated-at: 2026-08-16
triggers:
  - 审视工作流
  - grill 工作区
  - 定期 grill
  - 压测工作流
  - 治理审计
---

# workspace-grill

> 本文是工作区治理审计与决策协议的单一真源。

## When（何时触发）

- 操作者明确要求审视 WORKFLOW、治理、BACKLOG 或定期 grill。
- 用户指定具体方案或文档要做设计压测时，走通用**追问式压测（grilling 协议）**，不加载本 skill。

## 三种模式

| 模式 | 触发示例 | 行为 |
| ---- | ---- | ---- |
| 建议模式（默认） | 「审视当前工作流」「定期 grill 一下」 | 只读审计；一般治理候选**最多 3 项**；不提问、不修改 |
| 决策模式 | 「对这些建议逐题 grill」 | 一次一个决策，附证据、选项、收益、复杂度、推荐答案；**提问采用 grilling 问法格式**（❓ 题目 + ➡️ 推荐答案，逐问收敛；一句引用不复制正文） |
| 落地模式 | 「按已确认结论落地」 | 仅执行已确认决策；按独立版本/批次修改、验证、review |

**高危问题例外**：确定存在的数据丢失、凭证泄露、越权生产操作等必须**全部报告**，优先进入安全阻断清单，不占一般候选的 3 项上限。安全项也不能自动修改，仍须授权。

## Inputs（审计源）

每轮先读（先 INDEX 后正文，不遍历全部 `src/`）：

```text
WORKFLOW.md / BACKLOG.md
自上次治理变更以来的 CHANGELOG.md 条目（只读该范围，不全文通读）
story/case/tech/research/workspace-optimize 的 INDEX.md 与 CURRENT.md
exps/INDEX.md / notes/INDEX.md / reference/INDEX.md
.agents/skills/INDEX.md / .tools/INDEX.md
涉及候选的真实脚本或代码
```

扫描基线 = 最近一次产生治理变更的 CHANGELOG 条目。无实质变化的审计**不** bump 版本、不写 CHANGELOG、不建独立报告。

## Steps（决策模式）

1. 读取审计源形成候选。
2. 每个候选记录证据表（观察 / 来源 / 发生次数 / 相关机会数 / 置信度 / 当前机制）。
3. 筛选：最多 3 项高价值候选；无实际证据不进入决策；与现有规则重复的合并。
4. 一次一个决策：给出证据、选项、收益（高/中/低）、复杂度（高/中/低）、推荐答案。由操作者确认。
5. 共同理解形成前不落地。

## Gates（门禁）

- `grep` 零结果只能表述为「在当前查询范围未观察到」，不能直接表述为「不存在」。
- 新机制必须说明替代、合并或简化了什么。
- 只有净增规则和同步点、没有消除旧复杂度的，默认不纳入。
- BACKLOG 命中阈值只代表「有资格进入决策」，不代表自动晋升。

## Outputs

- 建议模式：≤3 项候选 + 证据表（不修改文件）。
- 决策模式：逐题决策记录（待操作者确认）。
- 落地模式：按已确认决策修改对应单一真源（WORKFLOW/Skill/AGENTS/BACKLOG/CHANGELOG），不 commit/push。

## grill 决策记录生命周期

grill 通过 **task 承载过程**（task README 决议 + CURRENT 进度），决策记录归档到 `workspace-grills/`（参照 `retrospectives/` 的冷层历史目录）：

- **过程承载**：grill 立项 `#workspace-optimize`（如 `workspace-optimize/task-YYYY-MM-DD-grill-...`），决议/分批/进度在任务 README + CURRENT；不在根目录创建独立的升级记录文件。
- **历史归档**：grill task review 通过、落地完成后，决策记录归档到 `workspace-grills/grill-<日期>.md`（历次清单见 `workspace-grills/README.md`）。
- **真源不反向引用**：任何真源（含 CHANGELOG）不得链接或「依据 grill-<日期>.md §X」指向它；想说明依据就写「按 grill 决议实施」。

## BACKLOG 证据与清理

- 每个候选只在真实命中或被纠正时追加最小证据引用（日期、任务链接、发生/机会判定）。
- 不维护脱离来源的手工汇总数字；从引用和任务 INDEX 重算。
- 前提已失效的候选（被引用机制退役 / 被 skill 覆盖）删除并在 CHANGELOG 记录失效原因；已被 Skill 覆盖的部分必须在 BACKLOG 注明，禁止重复计数。

## Verify

- 落地后跑 `python .tools/workspace-check.py`，errors 必须为 0；warning 逐条处置（修复/接受+理由/转 BACKLOG）。
- 改动带 frontmatter 的文档同步 `updated-at`。
