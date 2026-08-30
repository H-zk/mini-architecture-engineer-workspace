---
created-at: 2026-08-29
updated-at: 2026-08-29
type: 主题定义（visual-themes）
---

# editorial｜暖纸出版（浅色）

杂志/出版物气质：米色暖纸底、衬线大标题、赭橙强调、双细线分隔。叙事型报告、阶段回顾、成长报告——内容以「文章」形态呈现时用。

## Design Tokens（注入 :root）

```css
:root {
  --bg: #faf6ef;
  --surface: #f3ecdf;
  --elevated: #fffdf8;
  --text: #2b2620;
  --muted: #7a6f5f;
  --border: #e2d8c3;
  --accent: #9a3412;
  --accent-weak: #f6e8dd;
  --rule: #c9bda3;
  --radius: 4px;
  --shadow: 0 1px 4px rgba(120, 100, 70, 0.1);
}
```

## 字体（系统栈，零外链）

- 标题（衬线）：`Georgia, "Times New Roman", "Songti SC", SimSun, serif`
- 正文（无衬线保屏读性）：`system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif`
- 引文/题记（衬线斜体）：同标题栈 + `font-style: italic`

## 组件要点

- 大标题：衬线、加大字号（正文 2.2 倍以上）、可配 `--accent` 短横线题注；H1/H2 下方可加双细线（`border-bottom: 3px double var(--rule)`）。
- 正文：行长控制（max-width ~70ch）、行高 1.75；段首可用 `--accent` 首字下沉（可选）。
- 引文块：`--surface` 底 + 衬线斜体 + 左右缩进，不用左边条。
- 数据卡片：`--elevated` 底 + `--border` 描边，数字用衬线大号（出版物图表数字惯例）。
- 页眉/页脚：细线分隔 + 小号 `--muted` 字，可做「刊头」式样。

## 图表色板（序列/分类，6 色，低饱和出版色）

`#9a3412` 赭（主）、`#3f6212` 橄榄绿、`#1e3a5f` 藏蓝、`#713f12` 棕、`#0f766e` 青、`#86198f` 绛紫。

## 注意

- 打印友好（浅底）；适合长文阅读，不适合高密度数据表格。
- 衬线标题在中文字体下依赖宋体系（SimSun/Songti SC），屏幕小字号时降级为无衬线亦可接受。
