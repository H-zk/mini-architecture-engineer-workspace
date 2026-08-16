---
created-at: 2026-08-16
updated-at: 2026-08-16
type: 项目 Skill 索引
maintainer: AI（人类 review）
---

# 项目 Skill 索引（.agents/skills/）

本目录是工作区**项目 Skill 的单一真源**。各 agent 工具按各自机制加载（支持项目级 skills 的工具自动发现；claude 经 `.claude/skills/` junction 桥；codex/copilot 等无自动发现的工具按 `AGENTS.md` 指引按需读 `SKILL.md`）；不建副本目录，换机重建见 `.tools/skill-bridge/`。每个 Skill 必须有合法 frontmatter（`name` 与父目录匹配）；执行流 skill 明确 触发 / Lifecycle / 步骤 / 门禁 / 产物 / 验证。

| Skill | 触发 | 一句话 | 入口 |
| ---- | ---- | ---- | ---- |
| feat-plan-research | `#feat` / `#需求` / 写开发计划 | 需求开发流：五态 Lifecycle + 全流程门禁（全景调研 → plan 确认才编码 → 交付三件套 → 审核 → 验证三分法） | [feat-plan-research/SKILL.md](./feat-plan-research/SKILL.md) |
| case-troubleshoot | `#case` / `#排查` CASE 排查 | CASE 标准流程与证据闭环（先锁失败接口 + 事实/假设分区 + 完成门禁 + 对客回复可选） | [case-troubleshoot/SKILL.md](./case-troubleshoot/SKILL.md) |
| tech-consult | `#tech` / `#咨询` 技术咨询 | 技术咨询流：澄清 → 知识库分层查证（涉及系统现状回 `src/` 核实）→ `answer.md` 结论先行 | [tech-consult/SKILL.md](./tech-consult/SKILL.md) |
| research-survey | `#research` / `#调研` 需求调研 | 需求调研流：定边界 → 代码锚定现状（无实现也是结论）→ `report.md` 方案对比与建议 | [research-survey/SKILL.md](./research-survey/SKILL.md) |
| workspace-ops | `#workspace-optimize` / `#工作区优化` / 单字词启动器 | 工作区迭代优化总入口：维护菜单（内置 5 + 扩展位 1）+ 两步交互 + 路由表 + 两态 Lifecycle（含 reopen） | [workspace-ops/SKILL.md](./workspace-ops/SKILL.md) |
| workspace-grill | 「审视工作流」「grill 工作区」「定期 grill」 | 工作区治理审计与决策协议（建议/决策/落地三模式） | [workspace-grill/SKILL.md](./workspace-grill/SKILL.md) |
| workspace-review | 「review 暂存区/工作区改动」「按主题拆 commit」 | 未提交变更评审 + 主题化提交操作流（四段式反馈 + 证据门槛 + 既有约定重核 + hunk 级拆分 + 完整性验证；仅本工作区仓库，不含 src/ 代码评审） | [workspace-review/SKILL.md](./workspace-review/SKILL.md) |
| workspace-learn | 「学习/对比/借鉴外部工作区」「同事库对比」 | 外部工作区学习沉淀：只读授权下沿演进证据链做双维度对比（对方**有** CHANGELOG 与任务历史），产出借鉴清单——只分析不自动落实、逐条裁决分流 | [workspace-learn/SKILL.md](./workspace-learn/SKILL.md) |
| notes-reinforcement | `#workspace-optimize 知识库加固` / 启动器选中该项 | 知识库加固：已结 CASE/需求 5 步反哺 notes（盲判先行 → 方案 → 对照 → 代码核实 → 反思去重，盲点优先成坑） | [notes-reinforcement/SKILL.md](./notes-reinforcement/SKILL.md) |

> 扩展位（维护仓库）模板未内置 skill，接入思路见 [GUIDE.md](../../GUIDE.md) §3；接入后在此表登记并同步 `workspace-ops` 路由表。

## vendor 的第三方 skill

vendor 判定标准、检测命令、lock 关系、管理命令、安装后安全确认 SOP 的单一真源：[VENDOR.md](./VENDOR.md)。

| Skill | 触发 / 依赖信号 | 来源 | 入 lock？ |
| ---- | ---- | ---- | ---- |
| grilling | 压测触发语（「relentless 追问式压测」/ grill 类词）；WORKFLOW §0 两道闸门、workspace-grill 决策模式问法格式的路由目标 | 开源仓库（**remote**；模板预置 git 跟踪副本） | ❌（预置副本；本机用 CLI 更新后生成） |

> vendor skill **随源、不改骨架**（含上游的 lint 风格差异，如代码块语言标记）——保持与上游逐字节一致是完整性校验的前提（见 [VENDOR.md](./VENDOR.md)）；`.agents/` 本就不在 workspace-check 的 markdownlint 扫描范围。

## references/ 子目录约定（渐进披露）

执行流 skill 可带 `references/` 收纳低频参考资料，SKILL.md 正文只留要点 + 必读时机：

- 只放「产出/创建特定产物前才需要」的规范细节（命名规范、结构模板等）；主流程步骤不外置。
- frontmatter 必填 `created-at` / `updated-at` / `type`；文件名 kebab-case。
- SKILL.md 内保留一句要点 + **必读时机** + 相对链接，不裸外置（保证读者知道存在与何时读）。

## 与其他容器的关系

- **`AGENTS.md`**：所有任务默认生效的安全红线 + Agent 编辑纪律（默认安全保护不依赖 Skill 是否命中）。
- **本目录**：特定任务命中的稳定多步骤流程；**`exps/`**：Why、失败案例、适用边界（Skill 的设计理由在 exps，执行步骤在 Skill）。
