# commands — 工作区级 `/命令` 显式入口

> `.agents/commands/*.md` 是**薄路由**：frontmatter 声明关联 skill + `$ARGUMENTS` 透传给 skill 执行，**不复制 SKILL 正文**（防双真源漂移）。命令清单以本目录文件为准。

## 薄命令原则

- 每个命令文件 = frontmatter（`description` / `argument-hint` / `skills`）+ 一句路由语 + `$ARGUMENTS`，尽量精简（超过 ~15 行 = 该瘦身或改 skill）；
- 命令与 skill **同步维护**：skill 改名 / 合并 / 退役时，对应命令文件同批处理；
- 需要多步流程 / 门禁 / 产物的能力**不建命令**，直接建 skill（命令只是入口糖）。

## frontmatter 字段

- `skills`：关联 skill 名（真源）；多 skill 用逗号分隔（首个为主）。
- `argument-hint`：调用提示（可选）。
- `description`：一句话用途（命令面板可见）。

## 同名命令与覆盖冲突

- 工作区级命令与用户级（`~/.agents/commands/` 等）同名时，按工具的优先级规则解析——**改工作区命令不生效时先查同名覆盖**；
- 工作区内同名命令唯一，新增前先查本目录防重；
- 命令名与 skill 名解耦（可多命令指向同一 skill 的不同入口姿态）。
