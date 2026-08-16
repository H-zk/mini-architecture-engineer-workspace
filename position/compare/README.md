---
created-at: 2026-08-16
updated-at: 2026-08-16
type: 对比记录归档说明
---

# compare/ — 对比记录

每次对比一个**登记对象**（同事库 / 开源参照）落一份记录，命名 `YYYY-MM-DD-vs-<对象>.md`：

- **头部锚定基线**：仓库 + 分支/tag + commit（短 SHA）+ 日期——结论只对该基线负责。
- **正文**：双维度对比报告（同事库）或架构单维度报告（开源项目）+ 分优先级借鉴清单。
- **尾部两节必填**：**定位新认知**（本次对比对 [position 定位基准](../README.md)有何新认知，无则记「无」）+ **操作者最终决定**（逐条裁决留痕）。

一次性未登记对象（操作者临时给出路径）的对比记录落任务目录 `learn-report.md`，不落本目录。流程真源 = [`colleague-kb-synthesis` skill](../../.agents/skills/colleague-kb-synthesis/SKILL.md)。
