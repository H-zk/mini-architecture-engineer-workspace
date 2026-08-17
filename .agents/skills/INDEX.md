---
created-at: 2026-08-16
updated-at: 2026-08-17
type: 项目 Skill 索引
maintainer: AI（人类 review）
---

# 项目 Skill 索引（.agents/skills/）

本目录是工作区**项目 Skill 的单一真源**。各 agent 工具按各自机制加载（支持项目级 skills 的工具自动发现；claude 经 `.claude/skills/` junction 桥；codex/copilot 等无自动发现的工具按 `AGENTS.md` 指引按需读 `SKILL.md`）；不建副本目录，换机重建见 `.tools/skill-bridge/`。每个 Skill 必须有合法 frontmatter（`name` 与父目录匹配）；执行流 skill 明确 触发 / Lifecycle / 步骤 / 门禁 / 产物 / 验证。命令入口（`/command` 调用）= 根 `.agents/commands/` 薄路由文件，不在此目录。

| Skill | 触发 | 一句话 | 入口 |
| ---- | ---- | ---- | ---- |
| feat-plan-research | `#feat` / `#需求` / 写开发计划 | 需求开发流：五态 Lifecycle + 全流程门禁（全景调研 → plan 确认才编码 → 交付三件套 → 审核 → 验证三分法） | [feat-plan-research/SKILL.md](./feat-plan-research/SKILL.md) |
| case-troubleshoot | `#case` / `#排查` CASE 排查 | CASE 标准流程与证据闭环（先锁失败接口 + 事实/假设分区 + 完成门禁 + 对客回复可选） | [case-troubleshoot/SKILL.md](./case-troubleshoot/SKILL.md) |
| tech-consult | `#tech` / `#咨询` 技术咨询 | 技术咨询流：澄清 → 知识库分层查证（涉及系统现状回 `src/` 核实）→ `answer.md` 结论先行 | [tech-consult/SKILL.md](./tech-consult/SKILL.md) |
| research-survey | `#research` / `#调研` 需求调研 | 需求调研流：定边界 → 代码锚定现状（无实现也是结论）→ `report.md` 方案对比与建议 | [research-survey/SKILL.md](./research-survey/SKILL.md) |
| workspace-ops | `#workspace-optimize` / `#工作区优化` / 单字词启动器 | 工作区迭代优化总入口：维护菜单（内置 4 + 扩展位 1）+ 两步交互 + 路由表 + 两态 Lifecycle（含 reopen） | [workspace-ops/SKILL.md](./workspace-ops/SKILL.md) |
| workspace-grill | 「审视工作流」「grill 工作区」「定期 grill」 | 工作区治理审计与决策协议（建议/决策/落地三模式） | [workspace-grill/SKILL.md](./workspace-grill/SKILL.md) |
| workspace-review | 「review 暂存区/工作区改动」「按主题拆 commit」 | 未提交变更评审 + 主题化提交操作流（四段式反馈 + 证据门槛 + 既有约定重核 + hunk 级拆分 + 完整性验证；仅本工作区仓库，不含 src/ 代码评审） | [workspace-review/SKILL.md](./workspace-review/SKILL.md) |
| colleague-kb-synthesis | 「对比同事库」「学习/对比/借鉴外部工作区」「对比开源项目」 | 外部对象对比与借鉴分析：同步锚定 + position 定位基准对照 + 双维度对比（同事库=工作流范式+知识侧重；开源=仅架构）→ 分优先级借鉴清单——只分析不自动落实、逐条裁决分流；一次性路径 = 临时只读授权 | [colleague-kb-synthesis/SKILL.md](./colleague-kb-synthesis/SKILL.md) |
| notes-reinforcement | `#workspace-optimize 知识库加固` / 启动器选中该项 | 知识库加固：已结 CASE/需求 5 步反哺 notes（盲判先行 → 方案 → 对照 → 代码核实 → 反思去重，盲点优先成坑） | [notes-reinforcement/SKILL.md](./notes-reinforcement/SKILL.md) |
| knowledge-base | `/knowledge-*` 命令族（create / update / merge-temp / improve / refactor / check / evolve） | src/ 项目级知识库管理框架：项目 `AGENTS.md ## 知识库` 章节声明结构（skill 不硬编码业务），主文档 + temp/ 增量笔记全生命周期；**仅服务 `src/` 下代码项目，不用于本工作区 `notes/`**（本区走 notes-reinforcement，防双载） | [knowledge-base/SKILL.md](./knowledge-base/SKILL.md) |
| agents-md-refiner | 语义命中（初始化/补全/精简项目 AGENTS.md）；feat 调研环节目标仓 AGENTS.md 缺失/过时时按需提议 | 项目 AGENTS.md 完善流：分析代码提炼对 Agent 真正必要的约定（P0/P1/P2 探索清单 + 章节规范 + ≤200 行篇幅控制），诊断报告经操作者确认后更新 | [agents-md-refiner/SKILL.md](./agents-md-refiner/SKILL.md) |
| guide | 「新手引导」「快速适配」「处理 GUIDE」/ `/guide`；首次会话闸门（AGENTS `onboard-state: 待引导`）强制触发 | 新手引导流：业务范围定调（单业务/产品线/公司全业务）→ 环境与仓库 → 占位落填 → 首任务验证，适配完成后 GUIDE 缩为退役存根 + 引用清理（可选连带退役自身）；明确跳过 = `已跳过` 永久豁免 | [guide/SKILL.md](./guide/SKILL.md) |

> 扩展位（维护仓库）模板未内置 skill，接入思路见 [GUIDE.md](../../GUIDE.md) §3；接入后在此表登记并同步 `workspace-ops` 路由表。
> `updated-at` 约定：**模板原生 skill** 带 `updated-at`、随改 bump（编辑纪律见 AGENTS「编辑文档」）；**引入型 skill 保持引入形态、不带该字段**——判定以仓库根 `skills-lock.json` 登记为准（现 grilling / show-me，规范见 [VENDOR.md](./VENDOR.md)）；lock 外的 skill（借鉴落地如 knowledge-base / agents-md-refiner、自建）均属模板原生，frontmatter 带 `updated-at`。bump 规则只作用于带该字段的文档。

## vendor 的第三方 skill

vendor 判定标准、检测命令、lock 关系、管理命令、安装后安全确认 SOP 的单一真源：[VENDOR.md](./VENDOR.md)。

| Skill | 触发 / 依赖信号 | 来源 | 入 lock？ |
| ---- | ---- | ---- | ---- |
| grilling | 压测触发语（「relentless 追问式压测」/ grill 类词）；WORKFLOW §0 两道闸门、workspace-grill 决策模式问法格式的路由目标 | `github.com/mattpocock/skills`（**remote**） | ✅（`skills-lock.json` 进基线；更新经 `skills update`） |
| show-me | 语义命中：讲解/可视化类任务（「讲清楚」「一眼看懂」「画个图」）；描述触发灵敏，自动加载即可，无需手动 | `github.com/humanlayer/skills`（**remote**） | ✅（`skills-lock.json` 进基线；更新经 `skills update`） |

> vendor skill **随源、不改骨架**（含上游的 lint 风格差异，如代码块语言标记）——保持与上游逐字节一致是完整性校验的前提（见 [VENDOR.md](./VENDOR.md)）；`.agents/` 本就不在 workspace-check 的 markdownlint 扫描范围。
> 安全确认回填（四步见 [VENDOR.md](./VENDOR.md)）：grilling（2026-08-16）内容审查 ✓（无 URL / 外发 / 凭证 / 注入模式）、文件清单 ✓（仅 SKILL.md + agents/openai.yaml）；**2026-08-17 上游比对 ✓**——经 skills CLI 重装恢复上游原版（此前源副本含 3 处本地标点改动、违反「随源逐字节一致」，lock 同步 `a16b2f66`；CLI 曾向 `.claude/skills`（顶掉 junction）与 `.zcode/skills` 误写真副本，已清理并重建桥、`.zcode/` 进 gitignore）；生成物审查待首次真实使用，补齐后更新本注。
> show-me 使用边界（注脚覆盖上游「生成后自动打开」默认）：默认**会话内展示**（Mermaid / 伪代码 / 表格等内联形式优先）；仅操作者明确要可视化报告时才生成 HTML（自包含、只落 `temp/`、不外链）；**任何情况不自动打开浏览器**，只报路径由操作者自访。安全确认（2026-08-16）：内容审查 ✓（纯指导，无 URL / 外发 / 凭证 / 注入模式）、文件清单 ✓（仅 SKILL.md）；完整性 = 源自经验证的上游一致副本字节复制，本仓直取上游 raw 比对待授权、生成物审查待首次真实使用，补齐后更新本注。

## references/ 子目录约定（渐进披露）

执行流 skill 可带 `references/` 收纳低频参考资料，SKILL.md 正文只留要点 + 必读时机：

- 只放「产出/创建特定产物前才需要」的规范细节（命名规范、结构模板等）；主流程步骤不外置。
- frontmatter 必填 `created-at` / `updated-at` / `type`；文件名 kebab-case。
- SKILL.md 内保留一句要点 + **必读时机** + 相对链接，不裸外置（保证读者知道存在与何时读）。

## 与其他容器的关系

- **`AGENTS.md`**：所有任务默认生效的安全红线 + Agent 编辑纪律（默认安全保护不依赖 Skill 是否命中）。
- **本目录**：特定任务命中的稳定多步骤流程；**`exps/`**：Why、失败案例、适用边界（Skill 的设计理由在 exps，执行步骤在 Skill）。
