# skill-bridge — Claude Code skills 桥（junction / symlink）

把 Claude Code 的 skill 发现目录 `.claude/skills/` 重定向到工作区**单一真源** `.agents/skills/`。

## 为什么需要

Claude Code 原生**只发现 `.claude/skills/`**，不扫描 `.agents/skills/`（其他工具的约定目录，本工作区的真源）。链接方式按平台二选一：

- **Windows**：symlink（`mklink /D`）需管理员权限/开发者模式 → 改用 junction（`mklink /J`，无需特殊权限），Node fs（Claude Code 是 Node 程序）实测可跟随：`isSymbolicLink:true` + `realpathExists:true`
- **macOS / Linux**：普通 symlink 即可，无需特权

触发语义同理只认 `description`（`when_to_use`），不认 `triggers`（实测 claude CLI 2.1.172）——`triggers` 保留给声明它的工具用，触发语义必须写进 `description`；迁移 skill 进本工作区时逐个核对 `triggers` 关键词是否已进 `description`。

## 用法

```powershell
# Windows
powershell -NoProfile -ExecutionPolicy Bypass -File .tools/skill-bridge/link-claude-skills.ps1
```

```bash
# macOS / Linux
bash .tools/skill-bridge/link-claude-skills.sh
```

**幂等**（两脚本同语义）：已是正确的链接 → 跳过；`.claude/skills` 被占用为非链接或指向他处 → **报错不擅自删**，要求人工确认。

## 换机 / 重 clone 后

1. clone 后链接不存在（`.claude/skills/` 在 `.gitignore`，环境特定）；
2. 运行对应平台脚本重建（Windows: `link-claude-skills.ps1` / macOS·Linux: `link-claude-skills.sh`）；
3. **重启 Claude Code**（官方：首次创建顶层 skills 目录需重启才生效）。

## 为什么不入 git

`.claude/skills/` 在 `.gitignore`：链接是环境特定的；且 Windows 下 `core.symlinks=false` 时 git 会**跟随 junction**，把 `.agents/skills/` 内容当成 `.claude/skills/` 下文件重复跟踪，污染单一真源。
