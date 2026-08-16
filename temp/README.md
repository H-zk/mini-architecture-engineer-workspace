# temp/ — 临时输出

存放**临时产物**：工具对比测试输出、中间结果、调试 dump、编码 review 工作区等。

## 规则

- **不进 git**（已在 `.gitignore` 排除）。
- 避免污染全局 `/tmp`——临时输出优先放这里，便于追溯。
- **用完即清**：任务收尾时（见 [WORKFLOW.md §7](../WORKFLOW.md)）清理本任务在 temp 的产物；有保留价值的移入对应任务目录。
- 写入建议放 `temp/<归属>/` 子目录（如 `temp/<task-id>/`），方便跨会话识别归属、安全清理。
- 不放需要长期保留的内容（那些进 `exps`/`notes`/`reference`）。
- `__pycache__` 等运行缓存不进此目录（根 `.gitignore` 已排除 `__pycache__`）。

## 校验

`python .tools/workspace-check.py --section temp` 会扫描非 `README.md` 的残留并告警。

## 当前内容

（用完即清——详见 [WORKFLOW.md §7](../WORKFLOW.md)）
