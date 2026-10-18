# {story} 着陆卡

> 本卡是**模板真源**（生成器 `.tools/sync-worktree-workspace.py` 的输入件，随父仓 `workspace-code-setting/` 维护）；生成到任务 worktree 的**渲染副本勿手改**——冲突以本模板为准，重新生成即可。

code-workspace 窗口内的会话读不到父级工作区规范——本卡只承载最低限度硬规则与真源指针，不是规范本体。

## 会话启动协议（第一动作）

1. 读 `CURRENT.md`（status / next / blocker）+ `README.md`；
2. 交叉验证（next 指向产物是否存在、worktree 状态是否匹配）；
3. 复述「上次到哪 + 下一步」请操作者确认；
4. 从 `next` 继续。

## 文件分工

- 进度/状态 → `CURRENT.md`；改动清单/验收证据 → `review.md`（审核后冻结）；
- 物化过程明细（授权 / git 操作 / 部署顺序 / review 轮次）→ `process-log.md`；
- 验证期问题 → `verify-issues.md`；任务全景与代码上下文表 → `README.md`。

## 分支规则（flow：{flow_name}）

{flow_rules}

## 每批次硬规则

1. 改代码后同步 `review.md`；
2. 验证中发现问题登记 `verify-issues.md`（不追加 `review.md`）；
3. 批次结束更新 `CURRENT.md`；
4. **未经操作者授权不 commit/push（红线）**。

## 通用门禁速查

> 渲染源 = 父仓 `WORKFLOW.md` §2 的 gate-quickref 块（一行一条）；生成器抽块渲染与 quickref 机检对账随工具批接入——当前为模板手工同步快照，滞后以真源为准。

- commit/push 须操作者**单批授权**（「继续 / 好的 / 我看看效果」类顺延语不构成授权）；push 一律显式 refspec 单分支，永不裸 push、永不 `--tags`；主分支绝对禁推。
- 基础副本（`src/<namespace>/<repo>` 主检出）严格只读——一切编辑发生在任务 worktree，含源仓 `AGENTS.md` 等规范文件在内。
- 状态翻转即换会话：翻转会话只做收场动作，新状态事项新会话（`@` 任务 `CURRENT.md`）开启。
- 收尾两道门禁：沉淀询问逐条提议（答「没有」才跳过）+ `workspace-check` `errors=0`——先机检后翻转。
- 沉淀先查 notes/exps 双 INDEX、合并优先，未命中先过未命中根因自查再立新条。
- worktree/分支清理须操作者明确授权；AI 不删分支，删 junction 绝不 `rm -rf`（递归删真源）。

## feat 门禁速查（feat 流任务适用）

> 渲染源 = 父仓 `.agents/skills/feat-plan-research/SKILL.md` 的 gate-quickref:feat 标记块（一行一条）；生成器抽块渲染与 quickref 机检对账随工具批接入——当前为模板手工同步快照，滞后以真源为准。

- 推送链顺序：推送请求先过注释清扫门禁 → 操作者授权 → review 抽检五问 → 执行推送；推送授权词 = 五问触发器，答不上停留 `待授权推送` 不推。
- `status` 只取五态纯枚举（进行中/编码中/审核中/验证中/已完成），`next` 只取本态受控菜单值（参数 `:` 后缀跟摘要）——自造状态/越界取值 = 机检 error。
- 交付四件套齐备才转 `审核中`（reviewable 工作区 + review.md 自检 + process-log.md 骨架 + status 枚举）——编码完成 ≠ 交付，交付 ≠ 收尾。

## 真源指针

- 工作流规范 / 安全红线：父工作区 `AGENTS.md`、`WORKFLOW.md`（本卡不复制其内容）；
- flow 定义：`workspace-code-setting/git-flows.yaml`；目标仓代码规范：该仓根 `AGENTS.md`（若有）。
