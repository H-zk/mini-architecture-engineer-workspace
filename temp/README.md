# temp/ — 临时输出

存放**临时产物**：工具对比测试输出、中间结果、调试 dump、编码 review 工作区等。

## 规则

- **不进 git**（已在 `.gitignore` 排除）。
- 避免污染全局 `/tmp`——临时输出优先放这里，便于追溯。
- **用完即清**：任务收尾时（见 [WORKFLOW.md §7](../WORKFLOW.md)）清理本任务在 temp 的产物；有保留价值的移入对应任务目录。
- **永久白名单**：`README.md`（本说明）与 `todo.md`（操作者常驻随手记）不适用「用完即清」——清理与校验一律跳过（机器真源 = `workspace-check.py` temp 分区 `allowed` 集合）。
- **任务物料放 `temp/<任务id>/` 子目录**（如 `temp/task-2026-08-30-xxx/`、`temp/feat-2026-08-13-xxx/`），方便跨会话识别归属、安全清理——`<任务id>/` 前缀目录为校验合规形态，不告警（收尾随清归收尾门禁管）。
- 不放需要长期保留的内容（那些进 `exps`/`notes`/`reference`）。
- `__pycache__` 等运行缓存不进此目录（根 `.gitignore` 已排除 `__pycache__`）。

## 校验

`python .tools/workspace-check.py --section temp` 扫描规则外残留并告警（规则内形态不报：`README.md`/`todo.md` 白名单、`temp/<任务id>/` 任务关联目录）。

## 当前内容

（用完即清——详见 [WORKFLOW.md §7](../WORKFLOW.md)）
