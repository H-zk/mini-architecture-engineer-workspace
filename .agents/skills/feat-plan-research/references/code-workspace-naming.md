---
created-at: 2026-08-16
updated-at: 2026-08-29
type: feat 交付门禁参考（.code-workspace 命名规范与 settings 骨架）
---

# .code-workspace folder.name 命名规范

> 本文件是 `feat-plan-research` 交付门禁「reviewable 工作区」的参考资料：创建或修改 `.code-workspace` 前必读（命名 + settings 骨架）。

## settings 骨架（最小集，手写 .code-workspace 必含）

- **模板真源**：[workspace-code-setting/setting-example.json](../../../../workspace-code-setting/setting-example.json)——优先用生成器 `.tools/sync-worktree-workspace.py`（自动 folder + 模板下发 + 着陆卡）；手写时按下述骨架；
- **双根结构**：`folders` = 文档根（`{ "path": ".", "name": "docs" }`）+ 各 worktree 根并置；
- **git 隔离三键**（防父仓/worktree 互相污染 SCM）：`"git.autoRepositoryDetection": true`、`"git.openRepositoryInParentFolders": "never"`（防父仓进 SCM）、`"git.repositoryScanMaxDepth": 6`（发现深层 worktree；更深路径按需调大）；
- **噪音收口**：`files.exclude`（node_modules/dist 等）、`search.exclude`（另含 lockfile 类）按需收口。
- 格式化/语言 settings 按目标仓技术栈与既有约定配置（不预置——目标仓 `AGENTS.md` 优先，勿建影子规范）。

## 格式

`${namespace} › ${project} · ${baseBranch}→${targetBranch}`

- `namespace` = worktree 路径里 `src/<namespace>/` 的顶层目录（区分不同侧：frontend / backend / sdk 等）。
- `project` = 仓库名或 worktree 目录名。
- `baseBranch` = 工作分支基于的分支（source ref）；`targetBranch` = 合并目标分支（review 后合并回的分支，**须先存在——不存在则先建 + 推送远端，再开始开发**）。
- 标准 feat 多为 `base=target`（`develop→develop`，冗余但统一）；发版 / 跨基准 `base≠target`。

例：`frontend › rtas-sdk · develop→develop`；发版形态如 `frontend › pay-sdk · master→release-20260917`。

## 字符红线

name **禁用 `/` 及 glob/extglob 元字符 `( ) * ? [ ] { } ! @ + |`**——`/`、`()` 会使 VS Code「在文件夹中查找」（`./<name>/…` 前缀字面匹配）scope 失效（搜不到 / 跨 folder 命中）。

多段分隔用非元字符编码：`›`（U+203A）、`·`（U+00B7）、`→`（U+2192）。

## 生效注意

改完 `.code-workspace` 必须 `Developer: Reload Window` 才生效。
