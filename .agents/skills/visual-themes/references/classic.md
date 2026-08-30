---
created-at: 2026-08-29
updated-at: 2026-08-29
type: 主题定义（visual-themes）
---

# classic｜中性净版（浅色）

白底、克制的中性灰阶 + 单一蓝色强调。最通用的一套：默认讲解、评审报告、任何不确定时的稳妥选择；打印友好（白底高对比）。

## Design Tokens（注入 :root）

```css
:root {
  --bg: #ffffff;
  --surface: #f6f8fa;
  --elevated: #ffffff;
  --text: #1f2328;
  --muted: #656d76;
  --border: #d0d7de;
  --accent: #0969da;
  --accent-weak: #ddf4ff;
  --radius: 8px;
  --shadow: 0 1px 3px rgba(31, 35, 40, 0.08);
}
```

## 字体（系统栈，零外链）

- 正文/标题：`system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif`
- 代码/数字：`ui-monospace, "Cascadia Code", Consolas, "Courier New", monospace`

## 组件要点

- 卡片：白底 + `--border` 1px 描边 + `--radius` + 轻阴影；标题栏可用 `--surface` 底。
- 表格：表头 `--surface` 底、行分隔线 `--border`；斑马纹可选（奇数行 `--surface`）。
- 代码块：`--surface` 底 + 1px 边框，等宽字体。
- 强调块（note/warning）：`--accent-weak` 底 + `--accent` 左边条 3px。

## 图表色板（序列/分类，6 色）

`#0969da` 蓝（主）、`#1a7f37` 绿、`#9a6700` 黄、`#8250df` 紫、`#cf222e` 红、`#bf8700` 橙——中低饱和，白底上对比充分。

## 注意

- 打印场景：背景色可能被打印设置剥离，关键信息不要只靠颜色区分（加符号/标签）。
