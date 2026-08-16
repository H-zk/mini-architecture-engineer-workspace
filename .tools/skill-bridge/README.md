# skill-bridge — Claude Code skills 桥（junction）

把 Claude Code 的 skill 发现目录 `.claude/skills/` 用 junction 重定向到工作区**单一真源** `.agents/skills/`。

## 为什么需要

Claude Code 原生**只发现 `.claude/skills/`**，不扫描 `.agents/skills/`（其他工具的约定目录，本工作区的真源）。Windows 下 symlink（`mklink /D`）需管理员权限/开发者模式 → 改用 junction（`mklink /J`，无需特殊权限），Node fs（Claude Code 是 Node 程序）实测可跟随：`isSymbolicLink:true` + `realpathExists:true`。

## 用法

```powershell
# 工作区任意位置即可（脚本自定位工作区根）
powershell -NoProfile -ExecutionPolicy Bypass -File .tools/skill-bridge/link-claude-skills.ps1
```

**幂等**：已是正确的 junction → 跳过；`.claude/skills` 被占用为非 junction 或指向他处 → **报错不擅自删**，要求人工确认。

## 换机 / 重 clone 后

1. clone 后 junction 不存在（`.claude/skills/` 在 `.gitignore`，环境特定）；
2. 运行本脚本重建；
3. **重启 Claude Code**（官方：首次创建顶层 skills 目录需重启才生效）。

## 为什么不入 git

`.claude/skills/` 在 `.gitignore`：junction 是环境特定的 link；且 `core.symlinks=false` 下 git 会**跟随 junction**，把 `.agents/skills/` 内容当成 `.claude/skills/` 下文件重复跟踪，污染单一真源。
