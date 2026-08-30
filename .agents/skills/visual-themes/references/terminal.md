---
created-at: 2026-08-29
updated-at: 2026-08-29
type: 主题定义（visual-themes）
---

# terminal｜终端风（深色）

黑绿终端气质：近黑底、磷光绿正文、青色提示符、全等宽。CLI 讲解、日志分析、CASE 排查链路——「这是一段会话/一次执行」的语义。

## Design Tokens（注入 :root）

```css
:root {
  --bg: #0c1210;
  --surface: #111a15;
  --elevated: #16221b;
  --text: #c8f2cf;
  --muted: #5f7a68;
  --border: #1f3a2b;
  --accent: #4ade80;
  --prompt: #22d3ee;
  --warn: #facc15;
  --error: #f87171;
  --radius: 4px;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}
```

## 字体（系统栈，零外链）

- 全局等宽：`ui-monospace, "Cascadia Code", Consolas, "JetBrains Mono", Menlo, monospace`（中文回退系统默认，混排时中文自动落到系统字体，可接受）
- 字号略小于常规主题（等宽视觉偏大），行高 1.6。

## 组件要点

- 终端窗口容器：`--surface` 底 + `--border` 描边 + 顶部红黄绿三点窗口钮（Unicode `●` 三色）+ 标题栏。
- 命令行：`--prompt` 色 `$` / `>` 提示符 + 命令白亮、输出 `--text`、注释 `--muted`。
- 状态色语义：成功 `--accent`、告警 `--warn`、错误 `--error`——日志行按级别着色。
- 分隔/装饰：box-drawing 字符（`┌─` `│` `└─`）做框架与树形结构，不用图形边框。
- 高亮块：`--elevated` 底 + 左侧 `--accent` `▍` 字符条。

## 图表色板（序列/分类，6 色）

`#4ade80` 绿（主）、`#22d3ee` 青、`#facc15` 黄、`#f472b6` 粉、`#a78bfa` 紫、`#fb923c` 橙。

## 注意

- 等宽全排版信息密度高，正文段落控制在短段；长文解说部分可切回无衬线（混排允许）。
- 打印不友好——需要打印选 classic/editorial。
