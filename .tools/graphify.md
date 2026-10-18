# graphify 使用指导

> 全语料知识图谱工具（`graphifyy@0.9.67`，uvx 按需，版本锚定 = 引入轮参照实测版，未实测环境首用时重核）。代码 → 知识图谱：社团发现 / god-nodes 枢纽 / graph.html 可视化。本区定位 = **全景调研按需件**；符号精确定位 / 调用链 / 影响面走 [`codegraph.md`](./codegraph.md)（同场对照结论：主战场 codegraph 全面占优——graphify 自然语言 query 靠词猜起点是结构性弱点，agent 消费形态下确定性符号查询可靠性高一个量级）。

## 何时用

- **全景结构理解**：新接手 / 调研某仓「分几块、枢纽是谁」——god-nodes + 社团 + graph.html 力导向图（给人看的结构图）。
- **跨仓图谱**：`merge-graphs` 合并多仓图（跨仓 HTTP/RPC 边界两件工具都不可达，合的是代码结构不是服务调用）。
- 大仓可跑（2K 文件量级实测分钟级出图；god-nodes 有枚举噪音，作线索不作结论）。

## ★何时不适用

- **符号定位 / 调用链 / 影响面**：→ [`./codegraph.md`](./codegraph.md)（快且精确）。
- **markdown 知识库检索**：→ [`./ripgrep.md`](./ripgrep.md)。
- **docs 语义层**：默认不启用（见红线节），纯代码快速路径为准。

## 调用口径（uvx 按需）

```bash
# 查询面（需先建图；**在目标仓根执行**——graph CLI 就近读 <目标仓根>/graphify-out/，在工作区根跑会查空；查询语义见下「查询坑」）
uvx --from graphifyy graphify god-nodes --top 10
uvx --from graphifyy graphify path "符号A" "符号B" --undirected
uvx --from graphifyy graphify explain "符号"

# 建图（初建无单命令——上游设计 = agent 按 skill.md 编排多步，驱动脚本固化如下）
# 在工作区根执行，产物落 <目标仓根>/graphify-out/（uv 隔离工程，graphifyy 版本随 uv.lock 钉死）
uv run --project .tools/graphify python .tools/graphify/build.py <目标仓根>
```

## 建图驱动

初建流水线由 [`graphify/build.py`](./graphify/build.py) 固化（复刻上游 skill.md v8 代码仓快速路径：detect → AST 零 LLM 抽取 → 空语义 → 合并 → 建图聚类报告），承载于 uv 隔离工程 [`graphify/`](./graphify/)（pyproject + uv.lock，`graphifyy==0.9.67` 钉死；venv 不进 git）。产物 = `<仓根>/graphify-out/`（graph.json / GRAPH_REPORT.md / 状态件），属工具产物目录——已进统一本地忽略铺装（[`src-git-excludes.txt`](./src-git-excludes.txt) + [`apply-src-git-excludes.py`](./apply-src-git-excludes.py)）。

## 查询坑（实测）

- 自然语言 `query` 靠词匹配猜 BFS 起点，通用词（CDN/VIEWER 类）会猜到无关文件——优先用精确符号名的 `path`/`explain`。
- `path` 默认有向，常「No directed path」——**`--undirected` 是常态用法**；结果经类节点中转属粗粒度路径（「同类两方法」级信息量）。
- `explain`/`affected` 遇同名歧义按提示带 `path::` 前缀或完整节点 id 重试。
- 输出是节点清单（src/loc 锚）非源码正文——源码仍需二次 Read。

## 红线与边界

- **禁 `graphify install` / 各平台 install 子命令**：写 agent 配置目录（`~/.agents/skills/`、AGENTS.md marker 块、PreToolUse hook）——本区消费形态锁定 CLI 直用。
- 代码层零 LLM 零外发；语义层（docs/papers/images）仅识别 `GEMINI_API_KEY`/`GOOGLE_API_KEY` 且无 key 不阻塞——**本区不设 key，走 code-only 快速路径**。
- 敏感文件三层防护自带（`.ssh`/`.aws`/`.gnupg` 目录全跳 + `.env*`/`id_rsa` 模式 + 关键词判定）——`.env.local` 体系不进图。
