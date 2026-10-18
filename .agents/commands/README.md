# commands — 工作区级 `/命令` 显式入口

> `.agents/commands/*.md` 是**薄路由**：frontmatter 声明关联 skill + `$ARGUMENTS` 透传给 skill 执行，**不复制 SKILL 正文**（防双真源漂移）。命令清单以本目录文件为准。

## 薄命令原则

- 每个命令文件 = frontmatter（`description` / `argument-hint` / `skills`）+ 一句路由语 + `$ARGUMENTS`，尽量精简（超过 ~15 行 = 该瘦身或改 skill）；
- 命令与 skill **同步维护**：skill 改名 / 合并 / 退役时，对应命令文件同批处理；
- 需要多步流程 / 门禁 / 产物的能力**不建命令**，直接建 skill（命令只是入口糖）；
- **命令族边界**：只承载高频显式操作入口；定期类工作（BACKLOG 清理等维护节奏项）**不建命令**——触发靠与 agent 正常对话即可，节奏真源在 [`workspace-ops` skill](../skills/workspace-ops/SKILL.md)；
- 新增 / 移除命令后同步更新下方「命令清单」表。

## frontmatter 字段

- `skills`：关联 skill 名（真源，可选——直跑脚本 / 纯路由命令省略）；多 skill 用逗号分隔（首个为主）。
- `argument-hint`：调用提示（可选）。
- `description`：一句话用途（命令面板可见）。

## 同名命令与覆盖冲突

- 工作区级命令与用户级（`~/.agents/commands/` 等）同名时，按工具的优先级规则解析——**改工作区命令不生效时先查同名覆盖**；
- 工作区内同名命令唯一，新增前先查本目录防重；
- 命令名与 skill 名解耦（可多命令指向同一 skill 的不同入口姿态）。

## 命令清单

| 命令 | 关联 skill | 用途 |
| ---- | ---- | ---- |
| `/workspace-optimize` | workspace-ops | 工作区维护与优化入口（维护菜单 / 自定义事项按 `#workspace-optimize` 标签立项） |
| `/review` | workspace-review | 本仓未提交改动评审与主题化提交（单任务收场自检同入口） |
| `/workspace-check` | —（直跑 `.tools/workspace-check.py`） | 工作区质量机检（errors/warnings 现值与分区明细） |
| `/workspace-kanban` | workspace-kanban | 会话内任务看板（活跃任务只读投影 + 定期项逾期提醒） |
| `/sprint-check` | sprint-iteration | 迭代边界判态与体检（白名单/门禁对照 + 动作归属） |
| `/guide` | guide | 新手引导（快速适配模板） |
| `/learn` | colleague-kb-synthesis | 外部对象对比与借鉴 |
| `/grill-me` | —（grill 路由） | 工作区治理审计入口 |
| `/show-me` | show-me | 讲解可视化 |
| `/knowledge-create` | knowledge-base | 初始化知识库或创建主文档 |
| `/knowledge-update` | knowledge-base | 任务完成后记录增量到 notes/temp/ |
| `/knowledge-merge-temp` | knowledge-base | temp/ 笔记汇总回主文档 |
| `/knowledge-improve` | knowledge-base | 根据最新代码更新主文档 |
| `/knowledge-refactor` | knowledge-base | 重构知识库结构 |
| `/knowledge-check` | knowledge-base | 知识库健康检查 |
| `/knowledge-evolve` | knowledge-base | 迭代 knowledge-base skill 自身 |
