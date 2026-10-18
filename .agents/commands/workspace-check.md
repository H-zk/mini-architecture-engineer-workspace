---
description: 跑工作区质量机检（workspace-check：errors/warnings 现值 + 分区明细）
argument-hint: "[任务目录名，可空——聚焦单任务；空则全量]"
---

执行 `python .tools/workspace-check.py` 并汇报结果：

- 带参数（任务目录名）→ 加 `--task <名>` 单任务聚焦；
- 无参数 → 全量；汇报口径：errors / warnings 现值与分区构成、与收尾门禁的对照（业务任务收尾 `errors=0` 前置）；
- warning 逐条分类说明（本轮修复 / 既有项），不笼统报数。

$ARGUMENTS
