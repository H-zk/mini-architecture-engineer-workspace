# codegraph 使用指导

> 代码符号知识图谱工具（`@colbymchenry/codegraph@1.6.0`，版本锚定）。给**代码库**建符号索引：搜函数/类/方法、查调用关系、分析改动影响面；可作为 MCP server 接 AI agent。本区**主战场工具**（符号精确定位 / 调用链 / 影响面）；全景分层与可视化走 [`graphify.md`](./graphify.md)。

## 何时用

- **代码符号检索**：按函数/类/方法名搜（`query`）——同名多定义直接给文件:行号 + 完整签名。
- **调用关系分析**：谁调了 X（`callers`）、X 调了谁（`callees`）。
- **影响面分析**：改某个符号会影响哪些代码（`impact`）、改动影响哪些测试（`affected`，支持 `git diff --name-only | codegraph affected --stdin`）。
- feat 调研读代码定位、CASE 排查追调用链：给某个代码库（`src/<项目>/`）先建索引再问。

## ★何时不适用

- **markdown 知识库找地址/内容**：只对代码符号建索引，对 markdown 无效 → 用 [`./ripgrep.md`](./ripgrep.md) 或 `grep`。
- **全景分层 / 枢纽可视化**：无全景能力 → 用 [`./graphify.md`](./graphify.md)。

## 调用口径（npx 按需，不全局装）

```bash
# 不 npm i -g：node 由 nvm 管，切版本即把全局包孤儿化；一律 npx 按需
# 遥测默认开，一律带 CODEGRAPH_TELEMETRY=0（匿名统计也不出上下文洁净区）
CODEGRAPH_TELEMETRY=0 npx -y @colbymchenry/codegraph@1.6.0 <command>
```

## 关键命令速查

| 任务 | 命令 |
| --- | --- |
| 首次建索引 | `init [path]`（在目标仓根执行） |
| 重建 / 刷新索引 | `index`（init 对已有索引只提示不重建） |
| 看索引状态 | `status [path]` |
| 搜符号 | `query <name>` |
| 谁调用了 X | `callers <symbol>` |
| X 调了谁 | `callees <symbol>` |
| 改 X 的影响面 | `impact <symbol>` |
| 改动影响的测试 | `affected [files...]` |
| 看 indexed 文件结构 | `files` |
| 构建任务上下文 | `context <task>` |
| 作为 MCP server | `codegraph serve` |
| 清理 stale lock | `codegraph unlock [path]` |

## 注意

- 针对**代码库**（`src/<项目>/`），不是 markdown 知识库。
- 首次 `init` 按代码规模耗时；已有索引要刷新用 `index` 重建。
- 代码库 clone 后建索引，便于追调用链。
