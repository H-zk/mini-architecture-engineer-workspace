---
created-at: 2026-08-16
updated-at: 2026-08-16
type: 同事项目同步
maintainer: 清单由人类维护 / 同步记录由 Agent 维护
触发: 按人类提醒执行（非周期性，不主动触发）
---

# 同事项目同步（colleague）

收录同事的同类工作区。与开源参照对象（[open-source.md](./open-source.md)）同构：登记 → 同步锚定 → 对比 → 分流，统一入口见 [position/README.md](./README.md)「对比体系」，流程真源 = [`colleague-kb-synthesis` skill](../.agents/skills/colleague-kb-synthesis/SKILL.md)。**仅当你提醒我同步某个项目时**，我才按本文件执行对齐与借鉴；非周期性、不主动触发，避免占用日常上下文。

## 分工与边界（清单人类维护 / 记录 AI 维护）

- **项目清单表（名称 / git 地址 / 关注点 / 状态）由人类维护**：你把同事项目的 git 地址填进来即可。
- **同步记录表由 Agent 维护**：每次同步后更新。
- 本文件清单区与记录区**分工**：Agent 可写「同步记录」区与执行同步动作，但**不得改动「项目清单」区的地址等内容**（清单由人类维护）。

## 同步流程（你提醒后执行）

1. 你点名要同步的项目（可指定单个，或「全部」）。
2. 我按地址**只读**拉取/浏览同事仓库，聚焦过程资产：`.agents/skills/`、`notes/`、`exps/`、`WORKFLOW.md`、`AGENTS.md`。
3. 提炼可借鉴点：方法论、踩坑经验、规范、技能、工作流改进。
4. **借鉴清单分流**（真源 = `colleague-kb-synthesis` skill：经操作者裁决两轨——立即优化 → 建 `#workspace-optimize` 任务；待观察 → 登记 `BACKLOG.md` 标 `来源 [colleague:<名称>]` + 触发信号），**不直接写 exps/notes/skill/WORKFLOW**。对比详情与操作者决定落 [compare/](./compare/)；本文件「同步记录」只记同步动作摘要 + 指向 compare 记录。
5. 更新「同步记录」：日期、本次摘要、借鉴去向。

## 取数方式

优先只读——浅克隆 `git clone --depth 1` 到 `temp/colleague/<名称>/`（`temp/` 不进 git，用完即清）；需长期保留的参照对象，落点由你指定。公开 GitHub 仓库也可用 API/检索工具，无需克隆。**同仓分支对象无需克隆**：`git fetch origin <分支>` 后用 `git log/diff origin/<分支>` 本地只读对比并锚定 commit。`src/` 是业务代码仓集合（你 clone 授权的项目），不放学习对象。

## 项目清单（人类维护）

| 名称 | git 地址 | 关注点 | 状态 |
| ---- | -------- | ------ | ---- |

## 同步记录（Agent 维护）

| 项目 | 上次同步 | 本次摘要 | 借鉴去向 |
| ---- | -------- | -------- | -------- |
