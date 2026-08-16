---
created-at: 2026-08-16
updated-at: 2026-08-16
owner: architecture-engineer-workspace
type: 工作流变更日志（冷层，仅追溯时读）
---

# CHANGELOG

倒序排列，最新在上。版本与本日志按**任务**计：一个任务收尾时统一 bump 一次 `WORKFLOW.md` version 并在此追加一条（概括该任务全部工作流变更）；跨任务的独立小修可独立 bump + 一条（口径见 [WORKFLOW.md §8](./WORKFLOW.md)）。

## v0.1.0 — 2026-08-16

开源模板 v0.1.0 全量入库：机制来自一个实战工作区的验证沉淀，业务中立、开箱即配，适配指南见 [GUIDE.md](./GUIDE.md)。本批四条主线：

- **治理核心文档**：AGENTS（角色 / 安全红线 / 行为准则）、WORKFLOW（任务分流、通用纪律、收尾双门禁、sprint-version 迭代锚、经验三级毕业）、README / GUIDE / HUMAN 三入口、BACKLOG 候选池与 `.markdownlint.jsonc` 规则真源。
- **执行流 skills**：五类任务 Lifecycle 状态机与全流程门禁（feat 五态；case / research / workspace-optimize 两态带 reopen 回边；tech 两态单步直达）与治理协议（workspace-grill / workspace-review / workspace-learn / notes-reinforcement；grilling 为 vendor 预置副本）。
- **工具链**：workspace-check 一致性检查（状态集真源下放至 skill frontmatter `states:`）、密钥「加载不读取」体系（load-env.sh / load-env.ps1 + `_env_loader.py`）、skill-bridge junction 桥。
- **任务与知识目录骨架**：五类任务根目录与 exps / notes / reference / retrospectives / workspace-grills 的 INDEX 空表。
