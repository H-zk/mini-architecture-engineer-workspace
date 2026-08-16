---
description: 讲解可视化：用最小视图讲清当前话题（会话内形式优先）
argument-hint: "[要讲清楚的话题，留空=当前话题]"
skills: show-me
---

用 `show-me` skill 可视化讲解。遵守 `.agents/skills/INDEX.md` vendor 表注脚的使用边界：默认**会话内展示**（Mermaid/伪代码/表格等内联形式优先）；仅操作者明确要可视化报告时才生成 HTML（自包含、只落 `temp/`、不外链）；**任何情况不自动打开浏览器**，只报路径。

$ARGUMENTS
