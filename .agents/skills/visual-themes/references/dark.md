---
created-at: 2026-08-29
updated-at: 2026-08-29
type: 主题定义（visual-themes）
---

# dark｜深色科技（深色）

深底系：蓝灰深底、高对比正文、亮蓝强调。屏幕阅读的技术图、链路/架构讲解；投影/夜间环境友好。

## Design Tokens（注入 :root）

```css
:root {
  --bg: #0d1117;
  --surface: #161b22;
  --elevated: #1c2128;
  --text: #e6edf3;
  --muted: #8b949e;
  --border: #30363d;
  --accent: #58a6ff;
  --accent-weak: rgba(56, 139, 253, 0.15);
  --success: #3fb950;
  --radius: 8px;
  --shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}
```

## 字体（系统栈，零外链）

- 正文/标题：`system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif`
- 代码/数字：`ui-monospace, "Cascadia Code", Consolas, "Courier New", monospace`

## 组件要点

- 卡片：`--surface` 底 + `--border` 描边；避免在深底上再叠深阴影，层次靠 surface 明度差。
- 表格：表头 `--elevated`；分隔线 `--border`；禁用纯白 `#fff` 行文字（用 `--text`）。
- 代码块：`--elevated` 底，代码高亮用下方色板。
- 强调块：`--accent-weak` 半透明底 + `--accent` 左边条。
- 大面积正文块保持 `--bg` 底 + `--text` 字（对比度 ~13:1），`--muted` 只用于次要标签。

## 图表色板（序列/分类，6 色）

`#58a6ff` 亮蓝（主）、`#3fb950` 绿、`#d29922` 黄、`#bc8cff` 紫、`#ff7b72` 红、`#39c5cf` 青——深底上均为高可见度色。

## 注意

- 打印不友好（深底耗墨且浏览器默认剥离背景）——需要打印的产物选 classic/editorial。
- 图片若为白底截图，外面包一层 `--surface` 圆角容器避免刺眼。
