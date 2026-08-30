---
created-at: 2026-08-16
updated-at: 2026-08-30
type: 开源参照对象
maintainer: 清单由人类维护 / 记录由 Agent 维护
触发: 按人类提醒执行（非周期性，不主动触发）
---

# 开源参照对象（open-source）

收录可对标学习的开源方法论/上下文工程项目（工作流框架、agent 方法论等）。与同事库（[colleague.md](./colleague.md)）同构：登记 → 同步锚定 → 对比 → 分流，统一入口见 [position/README.md](./README.md)「对比体系」，流程真源 = [`colleague-kb-synthesis` skill](../.agents/skills/colleague-kb-synthesis/SKILL.md)。

## 锚定规则（与同事库的关键差异）

- **锚定 latest stable release tag**（排除 rc/beta/next 等预发布与开发分支）——release 才是经过验证的稳定可比态，开发分支含未发布改动，对比会吸收未定型内容。
- **无 stable tag 的回退**（2026-08-18 补充，源自四仓对比轮首例）：对象无任何 release tag 时，回退锚 main@<短 SHA> 并在记录头部显式注明回退原因与日期；活跃仓加注「结论时效性弱于 tag 锚定，仅对该 SHA 负责」，演进证据评估相应降权。
- **对比单维度**：仅架构/范式（组织方式、门禁与状态机写法、提示词资产结构与复用、上下文管理策略）——无业务重叠，知识侧重维度不适用。

## 取数方式

浅克隆公开仓库到 `temp/_open-source/<名称>/`（`temp/` 不进 git，用完即清）：`git clone --depth 1` 后 `git fetch --depth 1 origin tag <tag>` 并 checkout 该 tag。需长期保留的参照对象，落点由你指定；`src/` 是业务代码仓集合，不放学习对象。

## 参照清单（人类维护）

> 2026-08-18 由操作者授权 Agent 首批登记 4 仓（裁决留痕：task-2026-08-18-advice-triage）。

| 名称 | 仓库地址 | 关注点 | 状态 |
| ---- | -------- | ------ | ---- |

## 对比记录（Agent 维护）

| 名称 | 锚定版本 | 本次摘要 | 借鉴去向 |
| ---- | -------- | -------- | -------- |
