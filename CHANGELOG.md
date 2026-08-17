---
created-at: 2026-08-16
updated-at: 2026-08-17
owner: architecture-engineer-workspace
type: 工作流变更日志（冷层，仅追溯时读）
---

# CHANGELOG

倒序排列，最新在上。版本与本日志按**任务**计：一个任务收尾时统一 bump 一次 `WORKFLOW.md` version 并在此追加一条（概括该任务全部工作流变更）；跨任务的独立小修可独立 bump + 一条（口径见 [WORKFLOW.md §8](./WORKFLOW.md)）。

## v0.1.2 — 2026-08-17

v0.1.1 后第二批迭代：新手引导闭环、GUIDE 易用性重构、vendor 真源治理与口径收敛（含 workspace-review 评审轮裁决）。本批四条主线：

- **新手引导机制**：新增 `guide` skill + `/guide` 命令 + AGENTS frontmatter `onboard-state` 闸门（待引导 → 已完成/已跳过，跨会话状态承载；跳过不影响纯任务协作）——业务范围定调 → 环境与仓库 → 占位落填 → 首任务验证，适配完成后 GUIDE 缩为退役存根 + 引用清理（可选连带退役 skill 自身）；README / HUMAN / GUIDE 同步挂快速通道入口。
- **GUIDE 四段式重构**：「三步上手」→ 环境与仓库 / 五类任务教程（按上手顺序，`#tech` 零前置首跑）/ 其他 / 占位清单总表；工单系统接入从 CASE 前置降级为可选增强（任一任务类型可用、CASE 来源渠道不限——工单/消息群/邮件皆合法），case-troubleshoot 与 customer-report 措辞同步。
- **vendor 真源治理**：grilling 经 skills CLI 重装恢复上游原版（此前源副本含 3 处本地标点改动、违反随源逐字节一致，lock 同步 `a16b2f66`）；CLI 多落点副作用回收——`.zcode/` 进 gitignore、workspace-check 新增 `--section skills` 真源单一性门禁（禁 `.zcode`/`.codex` 副本目录 + `.claude/skills` 桥 realpath 校验）、VENDOR.md 增「安装后清理」三步 SOP。
- **口径收敛（评审轮裁决）**：引入型 skill（vendor：grilling/show-me；配套引入：knowledge-base/agents-md-refiner）`updated-at` 约定成文于 skills INDEX（不带该字段、保持引入形态；模板原生 skill 带并随改 bump）；学习源节奏口径回归 `position/` 登记表（workspace-ops 去双写、retrospectives 指针同步）；GUIDE 维护菜单项数修正（内置 4 + 扩展位 1）；`.tools/INDEX.md` 恢复 `--task`/`--staged` 能力描述。

## v0.1.1 — 2026-08-16

v0.1.0 后首批机制迭代：对比体系升级、三个新 skill 接入、命令入口层与 commit 前机器门禁。本批四条主线：

- **对比体系重构**：`workspace-learn` 升级为 `colleague-kb-synthesis`（新增开源参照对象、增量/全量对比模式与定位偏移裁决）；新增 `position/` 定位基准层（同事库/开源参照登记 + `compare/` 对比留痕）；阶段回顾机制闭环 4→5 项（新增定期项节奏核对）。
- **新 skill 接入与 vendor 治理**：`agents-md-refiner`（项目 AGENTS.md 完善流）、`knowledge-base`（src/ 项目知识库框架，`command/` 单一真源 + 根薄路由）、vendor 接入 `show-me`（会话内展示优先、不自动开浏览器）；`skills-lock.json` 进 git 基线，grilling 更新至上游最新。
- **命令入口层**：新增 `.agents/commands/` 薄路由 ×12（`/grill-me`、`/learn`、`/review`、`/show-me`、`/workspace-optimize`、`/knowledge-*` ×7）——frontmatter 声明关联 skill + `$ARGUMENTS` 透传，不复制 SKILL 正文。
- **机器门禁**：workspace-check 新增 `--staged` 暂存集聚焦（lint-staged 式 commit 前门禁，workspace-review 同步接入）；`.env` 纳入明文密钥与 URL 内嵌凭证扫描。

## v0.1.0 — 2026-08-16

开源模板 v0.1.0 全量入库：机制来自一个实战工作区的验证沉淀，业务中立、开箱即配，适配指南见 [GUIDE.md](./GUIDE.md)。本批四条主线：

- **治理核心文档**：AGENTS（角色 / 安全红线 / 行为准则）、WORKFLOW（任务分流、通用纪律、收尾双门禁、sprint-version 迭代锚、经验三级毕业）、README / GUIDE / HUMAN 三入口、BACKLOG 候选池与 `.markdownlint.jsonc` 规则真源。
- **执行流 skills**：五类任务 Lifecycle 状态机与全流程门禁（feat 五态；case / research / workspace-optimize 两态带 reopen 回边；tech 两态单步直达）与治理协议（workspace-grill / workspace-review / workspace-learn / notes-reinforcement；grilling 为 vendor 预置副本）。
- **工具链**：workspace-check 一致性检查（状态集真源下放至 skill frontmatter `states:`）、密钥「加载不读取」体系（load-env.sh / load-env.ps1 + `_env_loader.py`）、skill-bridge junction 桥。
- **任务与知识目录骨架**：五类任务根目录与 exps / notes / reference / retrospectives / workspace-grills 的 INDEX 空表。
