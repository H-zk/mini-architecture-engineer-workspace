---
created-at: 2026-08-16
updated-at: 2026-10-18
owner: architecture-engineer-workspace
type: 工作流变更日志（冷层，仅追溯时读）
---

# CHANGELOG

倒序排列，最新在上。版本与本日志按**任务**计：一个任务收尾时统一 bump 一次 `WORKFLOW.md` version 并在此追加一条（概括该任务全部工作流变更）；跨任务的独立小修可独立 bump + 一条（口径见 [WORKFLOW.md §8](./WORKFLOW.md)）。

机制类条目**落笔即标成熟度三态**——**定型**（已验证、按现状执行）/ **试行**（带日落或复查判据的实验态）/ **退役**（声明下线、留档原因）；试验允许，但不许无声；盘点口径见 [retrospectives/README.md](./retrospectives/README.md) 第 5 项。

## 2026-10-18（v0.2.0 → v0.3.0）

v0.2.0 后第四批迭代（结构性大改进位 minor）：迭代边界状态机、归档根收拢、经验毕业台账制与能力扩容。本批五条主线：

- **迭代边界状态机（引进定型）**：新增 `sprint-iteration` skill——三态（开始/中/结束）+ 结束批五阶段十六步 + tag 七门禁 + 开始批六步，WORKFLOW §2.7 收敛为元定义；WORKFLOW frontmatter 增 `sprint-version` 唯一真源字段与 `sprint-log` 掉落轨迹（机检：格式 + 尾段一致）；retrospectives 改两段式（A 段九步硬锚点 + B 段七层清算按需深浅）；`/sprint-check` 判态命令；ARCHITECTURE §3 度量升级六字段 + CURRENT 打标前移。
- **归档根收拢（定型）**：归档布局 `<任务根>/archive/` 收拢为根级 `archive/<根>/`（全工作区唯一归档根，冷层）；workspace-check 判定统一 `_in_archive`/`_task_type_of`（含旧布局残留三路径一致告警）、lint 负 glob 收敛 `!archive/**`、新增根内残留与散落归档根 warning。
- **经验毕业台账制（定型）**：再犯计数改追加式台账 `exps/TRIGGERS.md`（发现与判定分层：疑似/确认/剔除三态），毕业即移行 `exps/ARCHIVE_INDEX.md`（留档/删档/部分毕业三分流）；沉淀判据卡四问 + 出口 gate；错误驱动召回引擎 `.tools/exp-lookup.py`；新立「知识层不回指经验层」红线（skills/.tools/notes 禁 exps 条目直链，检索走 INDEX）。
- **feat 执行流增密（定型）**：review 抽检五问（推送授权前置门禁）、契约快照三要素升五轴冻结、mock 联调纪律、注释先行、归属判断五环溯源、大需求三形态产物；新增 6 个 references 细则（评审纪律/注释清扫/归属溯源/跨端对齐/重做对照/验证缺陷环）；着陆卡门禁速查区（gate-quickref 双标记块，当前手工同步快照）。
- **能力扩容与收场口径（定型）**：新增 skill——series-phase-task-manage（大任务系列容器）、diagram-conventions（产图约定）、plainness-check（平实度终检，配词表 `.tools/plainness-lexicon.md`）、workspace-kanban（会话内看板，与开工汇报共用扫描配方）；workspace-ops 增 skill 市场巡检项（三源取数 + 画像预筛）；新工具——rollout-extract（会话原文转录，自评一手证据源）、html-render-audit（CDP 渲染验收）、warnings-registry（机检豁免台账）、graphify 建图工程（uv 隔离）、apply-src-git-excludes（src 仓忽略铺装）、codegraph 版本锚定 npx 口径；skill-bridge `-Verify` 只读核验；收场四件④改「止于评审修复不提交」——提交推送归操作者统一会话（workspace-review 两种消费形态 + commit-splitting 细则件）。

## 2026-08-30（v0.1.2 → v0.2.0）

v0.1.2 后第三批迭代（结构性大改进位 minor）：架构评分体系引进、feat 规格判定增密、机器门禁大升级与 skill 扩容。本批五条主线：

- **架构能力反思体系（引进定型）**：新增顶层文档 `ARCHITECTURE.md`——架构师职责/方法论共识 + 五维能力评分 + 业务任务反思触发点表（单一真源在其 §5，WORKFLOW §7 与各执行流 skill 只留指针；feat 主记录前移至「审核中 → 验证中」且非阻断，case/tech/research 挂收尾阻断）。
- **feat 规格判定与交付增密**：feat-plan-research 新增规格判定（复杂度画像五维两档，判定是分流不是门禁）；大需求触发契约快照 + 增强项白名单两道增强门禁，配设计对照、任务全景、契约快照三个条件模板；交付三件套升级**四件套**（新增 process-log.md，CURRENT 回归 digest）。WORKFLOW 同步：收场三件升**四件**（新增主动提议主题化提交）、任务 README H1 记目录名机检、INDEX 纪律（workspace-optimize 入索引体系 + 摘要禁嵌易变状态）、subAgent 协议补「中断即部分执行态」、坑条目三档判据、§8 bump 条目头格式约定。
- **机器门禁升级**：workspace-check markdownlint 转 error 并扩围 `.agents/skills/**`（vendor 经 skills-lock 判定豁免、archive 冻结豁免）；新增 plainness（平实度四指标）、coverage、INDEX 对齐、README H1、next 受控菜单校验分区；`--staged` 暂存集聚焦三模式口径对齐；配套 46 个单元测试（`.tools/_tests/`）+ GitHub Actions CI 托底（个人工作区可删 `.github/`）。新增运维工具：context-usage（上下文占用探针）、repo-family（分支家族分析）、sync-worktree-workspace（worktree 工作区与着陆卡生成器，模板真源 `workspace-code-setting/`）、skill-bridge bash 版 link 脚本。
- **新 skill 扩容与目录机制**：新增五 skill——external-article-analysis / skill-fit-eval（外部输入分析姊妹对，判据真源共用）、repo-maintenance（「维护仓库」由扩展位兑现内置，五阶段骨架 + 【模板占位】）、tools-entry（小工具登记簿）、visual-themes（HTML 主题库）；INDEX 立「执行流 / 路由覆盖层 / vendor」骨架三档规则。新增 `reference/branch-flows.md`（基准分支判定真源）、`workspace-code-setting/` 五件套、retrospectives 分层快照模板与 grill 归档结构契约；BACKLOG 补触发信号行（2/2 满格升格）、分诊两轨、90 天日落；AGENTS 补工作区仓自身 git 写红线、会话汇报平实口径、vendor 边界条款。
- **评审收尾轮（workspace-review）**：HUMAN 补反思门禁人类侧（收尾 grilling 反问说明）与工具兼容速查；GUIDE 维护菜单口径对齐 5 项 + 能力总览补外部输入分析两行；AGENTS worktree 细则外迁（细则真源 = feat skill `references/worktree-protocol.md`，AGENTS 留红线摘要）；workspace-check `--task` 归档冻结豁免补齐、NEXT_MENU 宽容全角冒号；repo-maintenance 等 skill 引用口径修复与 `src/.editorconfig` 防火墙文件落地；新增 `CONTRIBUTE.md` 贡献机制说明（fork 分发 · PR 作同事库参考回流，不直接合入）。

> 成熟度：本批机制条目均为**定型**（源仓验证后引进或随门禁实测落地）。

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
