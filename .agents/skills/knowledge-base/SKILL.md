---
name: knowledge-base
description: 通用知识库管理技能。当需要初始化项目业务知识文档、在代码变更后记录增量知识、定期校验文档与代码一致性、重构知识库结构、或迭代优化 skill 自身时使用此技能。通过 /knowledge-create、/knowledge-update、/knowledge-merge-temp、/knowledge-improve、/knowledge-check、/knowledge-refactor、/knowledge-evolve 命令操作。
updated-at: 2026-08-29
---

# 知识库管理技能

通用知识库框架，用于在项目根目录 `notes/` 下组织业务/技术知识文档。知识库由**主文档**和 **temp 增量笔记**两部分组成。

项目通过 `AGENTS.md` 的 `## 知识库` 章节声明知识库的目录结构和文档列表，本技能提供操作这些文件的命令和工作流。

## 核心概念

### 知识库目录

```text
notes/                  # 知识库根目录（项目根目录下）
  {编号}-{名称}.md      # 主文档：按业务/技术域组织的结构化知识
  ...
  temp/                 # 临时增量笔记目录
    {序号}-{描述}.md    # 单次变更的增量记录
```

- **主文档**：长期维护的结构化知识，由项目在 AGENTS.md 中声明文件列表
- **temp/**：任务完成后的增量记录，定期汇总回主文档

### 与 AGENTS.md 的关系

项目的 `AGENTS.md` 中必须包含 `## 知识库` 章节，声明：

1. 知识库目录位置
2. 主文档列表（编号 + 文件名 + 说明）
3. 文档格式规范
4. 业务域到文档的映射关系（用于查阅）

本技能**不硬编码**任何具体的文档列表或业务映射——这些由项目 AGENTS.md 定义。

## 典型工作流

### 任务完成后的增量更新

1. 完成涉及业务逻辑变更的任务
2. 执行 `/knowledge-update`，将变更记录到 `notes/temp/`
3. 当 temp 文件 ≥5 个时，执行 `/knowledge-merge-temp`

### 定期维护

1. 每 30 天执行 `/knowledge-check`
2. 根据报告执行 `/knowledge-improve` 更新过时文档
3. 必要时执行 `/knowledge-refactor` 重构结构
4. 发现反复出现的同类问题时，执行 `/knowledge-evolve` 迭代 skill 自身

### 初始化新项目知识库

1. 在 `AGENTS.md` 中添加 `## 知识库` 章节
2. 执行 `/knowledge-create` 生成所有主文档

## 命令

| 命令 | 用途 |
|------|------|
| [`/knowledge-create`](./command/knowledge-create.md) | 初始化知识库或创建单个主文档 |
| [`/knowledge-update`](./command/knowledge-update.md) | 任务完成后记录增量变更到 temp/ |
| [`/knowledge-merge-temp`](./command/knowledge-merge-temp.md) | 将 temp/ 下的笔记汇总合并回主文档 |
| [`/knowledge-improve`](./command/knowledge-improve.md) | 根据最新代码更新已有知识库主文档 |
| [`/knowledge-refactor`](./command/knowledge-refactor.md) | 重构知识库结构（拆分/合并/重组文档） |
| [`/knowledge-check`](./command/knowledge-check.md) | 检查知识库健康度（是否落后于代码、是否需要重构） |
| [`/knowledge-evolve`](./command/knowledge-evolve.md) | 审视 skill 自身，基于使用痕迹发现局限性并迭代改进 |

命令的完整定义（参数、执行步骤、输出格式）在 `command/` 子目录，是各命令的单一真源；根 `.agents/commands/` 同名文件是薄路由入口，指向这里、不复制定义。

## 健康检查机制

每个主文档在末尾维护一个元数据块，记录最后检查和最后更新的时间：

```markdown
<!--
last-checked: 2026-05-22
last-updated: 2026-05-22
-->
```text

- `/knowledge-check` 执行时会读取并更新 `last-checked`
- `/knowledge-improve` 执行时会更新 `last-updated`
- `/knowledge-create` 创建文档时写入当天日期作为初始值
- `/knowledge-check` 至少每 **30 天** 执行一次（通过 `last-checked` 判断）

## 平台注意事项

### 文件读写编码（Windows）

知识库文档为**无 BOM 的 UTF-8** 编码。在 Windows 上操作这些文件时：

- **必须使用 Node.js** 的 `fs.readFileSync`/`fs.writeFileSync` 配合 `'utf8'` 编码参数
- **禁止使用 PowerShell 5.1** 的 `Get-Content` + `Set-Content` 组合，它会破坏无 BOM 的 UTF-8 文件编码
- **禁止使用** `[System.IO.File]::ReadAllText()` + `[System.IO.File]::WriteAllText()` 配合 PowerShell 字符串操作，同样的编码问题

正确的文件修改模式（Node.js）：

```javascript
const fs = require('fs');
const fp = 'notes/01-{模块名}.md';
let content = fs.readFileSync(fp, 'utf8');
content = content.replace('old text', 'new text');
fs.writeFileSync(fp, content, 'utf8');
```

如果需要执行多步替换，建议将 Node.js 脚本写入临时文件后执行，避免 `node -e` 中反引号转义问题。

## 文档模板与规范

模板和编写规范存放在 skill 的 `references/` 目录下：

- `references/doc-template.md` — 主文档格式模板（含变更历史章节和元数据块）
- `references/temp-template.md` — temp 增量笔记模板（含变更类型字段）
- `references/writing-guidelines.md` — 文档编写规范（含交叉引用原则）

创建或更新文档前，先读取对应的模板文件。`/knowledge-check` 可使用 `scripts/validate-knowledge.js` 进行确定性校验。
