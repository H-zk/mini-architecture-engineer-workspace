---
created-at: 2026-08-16
updated-at: 2026-10-18
---

# HUMAN — 操作者 SOP

> 本文档是**人类操作者**与工作区交互的标准操作流程。
> 定位：既不是 `exps/`（AI 经验沉淀）、也不是 `notes/`（业务知识），而是**人类上手与操作这个工作区的说明书**（首次适配见 [GUIDE.md](./GUIDE.md)，日常使用见本文 §1+）。

---

## 0. 首次上手（第一次接触工作区）

### 0.1 工作区怎么运作

工作区是「**人 + AI 协作**」：你是指挥，AI 是执行——你用标签发起任务，AI 立项/调研/开发（只编辑不提交），你 review 后提交，收尾沉淀经验。**完整心智模型（流程图 + 要点）见 [README](./README.md)「这是什么」。**

### 0.2 最小上手（零凭证即可协作）

1. 装一个支持项目级 skills 的 AI 工具，用它**打开本工作区** → `.agents/skills/` 里的项目 skill 自动加载，无需手动安装。工具兼容速查：支持项目级 skills 的工具直接可用；**claude 需先跑 `.tools/skill-bridge/` 的 junction 桥脚本**（首次 clone 就要跑，不只换机器时）；codex / copilot 等无自动发现的工具靠 AGENTS 指引按需读取，同样可用。
2. 发一个标签任务试试，例如 `#tech <业务问题>` → AI 自动建目录、查 `notes/`、调研、产出结论。

> **纯任务协作不需要任何凭证**。AI 只编辑文件、不提交；你 review 后手动 `git commit/push`。首次适配（环境与仓库 / 五类任务接入）见 [GUIDE.md](./GUIDE.md)；想更快就对 AI 说「新手引导」或发 `/guide`，它带你一次走完。**拉下仓库后的首次会话，AI 会自动发起新手引导**（业务范围定调起步）；明确说「跳过」则不再打扰，随时 `/guide` 回来。

### 0.3 按需增强（用到什么配什么）【模板占位：按你的环境补全此表】

| 想用的能力                       | 需要配什么                                                       |
| -------------------------------- | ---------------------------------------------------------------- |
| 工单直查（任一任务类型查工单）  | 你的工单系统 MCP / CLI 接入（思路见 [GUIDE](./GUIDE.md) §3.4）  |
| 日志 / DB / 配置查询类排查       | 对应查询入口的凭证，进 `.env.local`                              |

密钥统一放 **`.env.local`**（不进 git、单一真源）：`cp .env .env.local` 后填真实值。AI 只「**加载**」、不「读取」它（详见 `.tools/env/README.md`）。

### 0.4 已有业务代码目录？

本工作区用固定的 `src/<namespace>/<repo>/` 存放代码（自包含、零配置、AI 直接可访问）。若你已有自己的代码目录，两种方式，都无需引入环境变量：

- **并存（推荐）**：`src/` 是工作区的独立副本（不进 git、各项目独立 repo），与既有目录互不干扰。对 AI 说「把 XX 仓库 clone 进来」按需拉取。
- **软链**（省磁盘）：`mklink /J src\<namespace>\<repo> <你的既有路径>`（Windows junction，不需管理员），既有代码不挪、`src/` 体系能直接用。

### 0.5 验证（确认就绪）

发一个 `#tech` 真问题（见 [GUIDE](./GUIDE.md) §2.1），跑通即就绪（完整判据另含全量机器检查 `errors=0`——新手引导自动跑，手动适配自查一次）；或发 `#workspace-optimize 审视工作流` 让 AI 做一次只读审计。

### 0.6 Skills 的自包含结构（本机配置）

- **Skills 统一物理收纳在 `.agents/skills/`**，入口登记见其 `INDEX.md`。无自动发现的工具（codex / copilot 等）由 `AGENTS.md`「skills 加载」指引主动读取。
- **换机器 / 新 clone**（Windows + claude 用户）：跑 `powershell -NoProfile -ExecutionPolicy Bypass -File .tools/skill-bridge/link-claude-skills.ps1` 重建 skills 链接，建议随后同命令加 `-Verify` 核验一次（检查 `.agents/skills` 真源与 junction 指向）；其余工具直接可用。
- **全局 config 保持不动（项目优先，全局兜底）**：项目级配置覆盖全局同名项，无需改全局即可工作；不删改各工具的全局配置。新增能力一律先落项目级（原则见 [AGENTS.md](./AGENTS.md)「配置」）。

---

## 1. 每次会话（启动检查）

打开工作区后，按顺序做：

1. **续接活跃任务**：对 AI 说「看看当前有哪些进行中的任务」→ AI 会 grep `CURRENT.md` 并汇报清单。
2. **选定任务**：从清单中挑一个继续，或发起新任务（见 §3）。
3. **如果无活跃任务**：跳到 §2 做定期维护，或直接发标签发起新任务。

> 提示：如果只是想闲聊或查资料，不用加标签，AI 不会建任务目录。

---

## 2. 定期维护（清单与节奏真源 = [`workspace-ops` skill](./.agents/skills/workspace-ops/SKILL.md)）

> 本节只承载**人类入口**（每项发什么）；维护项清单、两步交互、节奏与依赖的唯一真源在 [`workspace-ops` skill](./.agents/skills/workspace-ops/SKILL.md)——新增/调整维护项只改 skill 一处，本表随需跟进入口描述（项数随 skill 演化，不在此计数）。

| 维护项 | 入口（对 AI 说） |
| ------ | ---- |
| 审视工作流 | `#workspace-optimize 审视工作流`（唯一 BACKLOG 评估者） |
| 阶段回顾 | `#workspace-optimize 做一次阶段回顾` |
| 学习外部工作区 | `#workspace-optimize 学习外部工作区 <本地路径>`（给出路径 = 只读授权；登记层 = `position/`，清单你维护） |
| 知识库加固 | `#workspace-optimize 知识库加固`（备已结 CASE/需求素材 + 查询入口） |
| 维护仓库 | `#workspace-optimize 维护仓库`（五阶段独立显式授权；配套脚本【模板占位】，接入后全量启用） |
| skill 市场巡检 | `#workspace-optimize skill 市场巡检`（存活候选清单呈你点名，点名项走单仓评估） |

### 2.1 工作流瘦身（workspace-grill）

发 `#workspace-optimize 审视工作流`：AI 按 `workspace-grill` skill 三模式执行——**建议**（只读审计，最多 3 项）、**决策**（一题一决策）、**落地**（仅执行已确认决策）；确认后更新 WORKFLOW + CHANGELOG。

### 2.2 阶段回顾（定期复盘执行质量）

实战线**硬锚点 = 迭代末**（template 线按需发起，不走迭代节奏——见 [WORKFLOW §2.7](./WORKFLOW.md) 豁免），发 `#workspace-optimize 做一次阶段回顾`：AI 锚定上一次回顾的 commit 到当前 HEAD，复盘「执行质量」（做对 / 做快 / 做扎实），产出 `retrospectives/retro-YYYY-MM-DD.md`。方法与节点锚见 [`retrospectives/README.md`](./retrospectives/README.md)。回顾为 BACKLOG / WORKFLOW 调整提供基于事实的输入，但遵循「宁可晚进」。回顾时顺带确认 [ARCHITECTURE.md](./ARCHITECTURE.md) §4 五维评分快照。

---

## 3. 任务发起（五类标准标签）

在对话**最开头**打标签（必须是消息第一个 token），AI 会自动建任务目录。**不确定用哪个，或想看某分类现状？单独输入分类词，AI 弹该分类快捷菜单 + 允许自定义输入：**

- `workspace-optimize` / `工作区优化` → **定期维护快捷入口**（见 §2）+ 自定义输入；
- `story` / `需求`、`case` / `排查`、`research` / `调研`、`tech` / `咨询` → 列出该分类**未完成**的任务，+ 自定义发起新任务。

| 标签                   | 用途           | 落地点                               |
| ---------------------- | -------------- | ------------------------------------ |
| `#feat` 或 `#需求`     | 需求开发       | `story/feat-YYYY-MM-DD-描述/`        |
| `#case` 或 `#排查`     | CASE 排查      | `case/case-YYYY-MM-DD-描述/`         |
| `#tech` 或 `#咨询`     | 技术咨询       | `tech/tech-YYYY-MM-DD-描述/`         |
| `#research` 或 `#调研` | 需求调研       | `research/research-YYYY-MM-DD-描述/` |
| `#workspace-optimize` 或 `#工作区优化` | 工作区迭代优化 | `workspace-optimize/task-YYYY-MM-DD-描述/` |

示例：

```text
#case 用户反馈下单后订单状态未更新，帮我排查
```

> 能即时回答的简单问题不要打 `#tech`，直接问即可。

### 3.1 状态翻转后接续任务（跨会话续接）

任务状态翻转后，AI 会在收场时输出**交接卡**（进入方式 + 首步动作 + 待决策点）。新状态事项两种接法：**你开新会话**（默认，需你交互/决策的段必须走这条；进入方式 = `@ <任务>/CURRENT.md`）或 **AI 派隔离执行单元**自主执行（仅限「决策已做完」的自主段，如 plan 确认后的编码段）。执行单元遇决策点会即停并留痕 CURRENT（看 `next`/`blocker`），你回来处理后开新会话继续即可。规则真源：[WORKFLOW.md §2.6](./WORKFLOW.md)「状态翻转的会话边界」。状态翻转收场时，AI 只做评审修复自检、不提交——改动保持 unstaged 攒批；你随时统一开一个会话，走 `workspace-review` 把攒批改动按主题提交推送。

---

## 4. 审核与收尾

### 4.1 代码审核

AI **不会 commit/push**。代码改动由你 review 后手动提交；review 通过后也可临时授权 AI 提交（授权一次性，执行后恢复默认限制）。

### 4.2 文档审核

AI 写的文档（story/case/tech/research 下的产出）需要你确认：

- 结论是否正确
- 是否需要沉淀到 `exps/` 或 `notes/`
- 任务目录是否可以归档

**提交前仪式（工作区变动，尤其含 workspace-optimize 任务的批次）**：提交前手动发起一次 workspace-review 会话（对 AI 说「review 工作区的改动」），走完结构化 review 流程（状态口径 → 分主题反馈 → 证据门槛 → `--staged` 机器检查）后再提交——比肉眼扫 diff 更有把控感，也是「人在环中」在提交边界的落点。触发语与流程见 `.agents/skills/workspace-review/SKILL.md`。

### 4.3 收尾

对 AI 说「这个任务完成了，收尾吧」→ AI 会执行收尾门禁（确认制完成 → 沉淀询问 → 工作区校验 errors=0）、更新 `CURRENT.md` 状态、更新 INDEX。**业务任务会反问你对本任务的看法**（做对什么 / 有无返工 / 验证情况），用于 `ARCHITECTURE.md` 评分观察——case/tech/research 收尾时是 grilling 反问的**阻断性门禁**（答完才继续收尾）；feat 主记录已前移至「审核中 → 验证中」转态时（非阻断提醒），收尾时仅简单咨询补充验证期信号。回顾时再顺带确认五维评分快照（§2.2）。

---

## 5. 能力速查（指针）

| 想做什么 | 去哪看 |
| -------- | ------ |
| 首次适配（填业务 / 接工单） | [GUIDE.md](./GUIDE.md) |
| 定期维护各项怎么触发 | 本文件 §2 |
| 各能力对应的 skill 与触发语 | `.agents/skills/INDEX.md` |
| 经验索引 | `exps/INDEX.md` |
| 业务知识索引 | `notes/INDEX.md` |
| 工作区变更日志 | `CHANGELOG.md` |
| 待验证改进 | `BACKLOG.md` |
