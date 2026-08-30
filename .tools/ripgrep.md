# ripgrep (rg) 使用指导

> 快速文本搜索工具（Rust）。比 grep 快 ~2.4×，TTY 智能颜色+行号，默认尊重 `.gitignore`。
> 本文件只讲「怎么调」；选型方法论（精确查询 vs 模糊查询、vs grep）按「先索引后正文」的读取纪律判断。

## 何时用

- 日常代码 / 文档搜索、大库检索（10 万行+ 优势放大）。
- 交互式（终端自动颜色 + 行号）；脚本/管道里需显式 `-n`。
- 正则检索。

## 安装

```bash
scoop install ripgrep     # Windows（已装，15.1.0）
# 或 cargo install ripgrep
```

## 关键命令速查

| 任务 | 命令 |
| --- | --- |
| 递归搜（默认跳过 `.gitignore`） | `rg "pattern"` |
| **普查（含被 ignore 的，如 `src/` 下独立仓库）** | `rg --no-ignore "pattern"` ★找仓库/线索普查必加 |
| 只搜某种类型 | `rg -t md "pattern"`（md）/ `-t py` / `-t java` |
| 带行号（脚本/管道） | `rg -n "pattern"` |
| 正则 | `rg "task-\d{4}-\d{2}-\d{2}"` |
| 上下文 | `rg -A2 -B2 "pattern"` |
| 只列匹配文件 | `rg -l "pattern"` |
| 大小写不敏感 | `rg -i "pattern"` |

## ★坑：默认会漏两类内容

rg 默认比 grep「干净」，但会**静默跳过**两类内容，普查时易漏：

1. **`.gitignore` 忽略的文件**：本工作区 `src/` 下若干 clone 进来的独立仓库被父 `.gitignore` 排除，rg 默认不搜（源仓实测：默认命中 vs `--no-ignore` 命中差可达两成以上）。
2. **`.` 开头的隐藏文件/目录**：如 `.claude/`、`.config/`——**rg 默认跳过隐藏目录**（源仓实测搜 git 相关内容，grep 与 rg 的差行全在 `.claude/skills/` 下）。

→ **穷尽搜索（找仓库/线索普查）**用 `rg -uu`（跨 ignore + 隐藏），或更彻底 `rg -uuu`（再含二进制）。`-u` 递进：`-u`=不忽略 gitignore，`-uu`=再含隐藏，`-uuu`=再含二进制。

## 普查封装（复制即用）

```bash
# 加到 shell rc：普查时用 rg-pu 代替 rg，自动跨 .gitignore
rg-pu() { rg --no-ignore "$@"; }
```

## 何时不用 rg

- 找精确仓库名/地址：`grep` 或 `rg` 都行。
- 模糊自然语言检索（如「踩过哪些某类坑」）：rg 只能关键词匹配，真要语义检索才考虑向量工具（本工作区暂无需求）。
