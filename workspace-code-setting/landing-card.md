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

## 真源指针

- 工作流规范 / 安全红线：父工作区 `AGENTS.md`、`WORKFLOW.md`（本卡不复制其内容）；
- flow 定义：`workspace-code-setting/git-flows.yaml`；目标仓代码规范：该仓根 `AGENTS.md`（若有）。
