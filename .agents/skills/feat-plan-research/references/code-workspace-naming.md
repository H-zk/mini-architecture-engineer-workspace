---
created-at: 2026-08-16
updated-at: 2026-08-16
type: feat 交付门禁参考（.code-workspace folder 命名规范）
---

# .code-workspace folder.name 命名规范

> 本文件是 `feat-plan-research` 交付门禁「reviewable 工作区」的参考资料：创建或修改 `.code-workspace` 的 folder name 前必读。

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
