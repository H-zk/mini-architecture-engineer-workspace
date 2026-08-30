---
created-at: 2026-08-29
updated-at: 2026-08-29
type: 主题定义（visual-themes）
---

# blueprint｜蓝图线框（深色）

工程蓝图气质：深蓝底 + 网格底纹 + 白色线框 + 黄色高亮标注。架构图、拓扑图、组件关系图专用——「这是一张工程图纸」的语义自带严肃感。

## Design Tokens（注入 :root）

```css
:root {
  --bg: #0f3a66;
  --grid: rgba(126, 169, 233, 0.12);
  --surface: rgba(18, 58, 110, 0.85);
  --text: #dce9f7;
  --muted: #9db8d6;
  --border: #4a7fb5;
  --wire: #7ec8ff;
  --accent: #ffd60a;
  --radius: 2px;
  --shadow: none;
}
```

## 网格底纹（主题标志，body 上）

```css
body {
  background-color: var(--bg);
  background-image:
    repeating-linear-gradient(0deg, var(--grid) 0 1px, transparent 1px 24px),
    repeating-linear-gradient(90deg, var(--grid) 0 1px, transparent 1px 24px);
}
```

## 字体（系统栈，零外链）

- 标注/正文：`system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif`
- 编号/坐标/技术标注：`ui-monospace, "Cascadia Code", Consolas, monospace`（小号 + 字间距 0.05em）

## 组件要点（线框语言，与卡片语言区分）

- 节点/组件框：**透明填充 + `--wire` 实线 1.5px 描边 + 直角**（`--radius: 2px`）；内部标题 + 等宽小标注（如 `svc-playback`）。
- 关系连线：`--wire` 实线/虚线（实线=同步、虚线=异步），箭头用内联 SVG；关键路径用 `--accent` 黄色加粗。
- 标注标签：等宽小号、大写英文或中文短语，可带图签框（右下角：图名/版本/日期，工程图纸惯例）。
- 分区边界：`--border` 虚线框 + 分区名标签（内外网/信任边界）。

## 图表色板（序列/分类，6 色）

`#ffd60a` 黄（主强调）、`#7ec8ff` 浅蓝、`#8ef0a5` 浅绿、`#ffb4a2` 浅红、`#d0a9ff` 浅紫、`#f7f0a1` 浅黄——深蓝底上均为高可见度色。

## 注意

- 文字密度控制：蓝图风格依赖留白与网格呼吸感，节点内文字两行以内。
- 只做架构/拓扑/关系类；数据报表类内容（表格为主）用 dark 更合适。
