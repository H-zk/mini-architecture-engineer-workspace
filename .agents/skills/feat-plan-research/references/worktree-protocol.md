---
created-at: 2026-08-30
updated-at: 2026-08-30
type: worktree 细则真源（三视图 / feature 分支 / 路径 / 着陆卡 / 清理）
---

# worktree 细则（代码视图隔离协议）

> AGENTS「代码视图隔离」的细则真源：AGENTS 留三视图概念与红线级摘要，本文承载执行细则。feat / case 任务进入 worktree 操作前必读；git 边界红线（不 commit/push、授权制）见 AGENTS 安全红线。

## 三视图（完整定义）

勿在同一 `src/<repo>` 用 `git switch` + stash 混载排查与开发：

1. **基础副本** `src/<namespace>/<repo>`：固定远端默认分支（线上核实，只读为主）。
2. **evidence-readonly worktree**：实际部署 commit ≠ 基础副本 HEAD → 建 detached 只读 worktree（`mode: evidence-readonly`）。
3. **development worktree**：需求开发 → 独立 development worktree（`mode: development`），**默认直接检出开发分支**（本地 `switch -c <开发分支> --track origin/<开发分支>`；基准分支 = 合并目标 = 检出分支 = 该仓活跃开发分支，三者同一）。

## feature 分支（仅限两场景）

命名 `feature/<UPPER-ID>-<short-desc>` 或 `feature/<type>-<日期>-<short-desc>`（CASE 修复同）；只作本地开发期隔离、**不推送**（见 AGENTS 安全红线）。两场景：

1. 合并分支即远端默认分支、被基础副本 worktree 占用（git 同分支双 worktree 互斥）；
2. 同仓多任务并行需分支隔离。

创建前先 `fetch`/`pull` 并确认开发分支远端存在，**落后于主分支先合并好再建**；任务中途基座漂移（远端有新提交）→ 提交前 `stash → ff-only 同步 → pop`。

## 路径与 MAX_PATH

- 路径模式：`src/.worktrees/<task>/<namespace>/<repo>`（保留完整 namespace；同步/校验脚本已跳过）。
- 超 `MAX_PATH` 260 用 ticket 号短别名替代全任务名（namespace 保留），不改 `core.longpaths`。

## 子窗口着陆卡

任务用独立 code-workspace / 子窗口会话时（读不到父级规范），用 `.tools/sync-worktree-workspace.py` 生成任务侧着陆卡 AGENTS.md（模板真源 `workspace-code-setting/`：最低硬规则 + 真源指针 + 会话启动协议；机制见其 README）。

## 任务 README 代码上下文表

`| 仓库 | 用途 | mode | source ref | base/evidence commit | working branch（默认=开发分支，fallback 标 feature） | 路径 |`

## 清理与禁止

- 移除需操作者明确授权，先证明 clean、无人使用、代码已提交/安全保管（AI 不删分支）。
- **禁止**：用 stash 在 worktree 间传递代码；让批量同步扫描 `.worktrees/`；在基础主分支副本直接开发需求。
