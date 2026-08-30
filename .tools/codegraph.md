# codegraph 使用指导

> 代码符号知识图谱工具（`@colbymchenry/codegraph`）。给**代码库**建索引，搜函数/类/方法符号、查调用关系、分析改动影响面；可作为 MCP server 接 AI agent。

## 何时用

- **代码符号检索**：按函数/类/方法名搜（`query`）。
- **调用关系分析**：谁调了 X（`callers`）、X 调了谁（`callees`）。
- **影响面分析**：改某个符号会影响哪些代码（`impact`）、改动影响哪些测试（`affected`）。
- 给某个代码库（`src/<项目>/`）建知识图谱；可作为 MCP server（`codegraph serve`）接 AI agent。

## ★何时不适用

- **markdown 知识库找地址/内容**：codegraph 是**代码符号**工具，对 markdown 不建符号索引，找 git 地址/经验内容无效 → 用 [`./ripgrep.md`](./ripgrep.md) 或 `grep`。

## 安装（已全局装）

```bash
npm i -g @colbymchenry/codegraph
```

## 关键命令速查

| 任务 | 命令 |
| --- | --- |
| 建初始索引 | `codegraph init [path]` |
| 增量同步变更 | `codegraph sync [path]` |
| 看索引状态 | `codegraph status [path]` |
| 搜符号 | `codegraph query <name>` |
| 谁调用了 X | `codegraph callers <symbol>` |
| X 调了谁 | `codegraph callees <symbol>` |
| 改 X 的影响面 | `codegraph impact <symbol>` |
| 改动影响的测试 | `codegraph affected [files...]` |
| 看 indexed 文件结构 | `codegraph files` |
| 构建任务上下文 | `codegraph context <task>` |
| 作为 MCP server | `codegraph serve` |
| 清理 stale lock | `codegraph unlock [path]` |

## 注意

- 针对**代码库**（`src/<项目>/`），不是 markdown 知识库。
- 首次 `init` 按代码规模耗时；之后 `sync` 增量。
- 代码库 clone 后建索引，便于追调用链。
