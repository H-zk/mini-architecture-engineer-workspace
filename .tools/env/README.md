# 环境变量与密钥注入约定

> 单一明文真源 = `.env.local`（gitignored）。所有 agent 工具和脚本统一「**加载**」密钥，而非「**读取**」明文。

## 核心原则：加载 ≠ 读取

| 操作 | 是否把明文打印进 agent 上下文 | 是否允许 |
| --- | --- | --- |
| `source .tools/env/load-env.sh` / `. .\.tools\env\load-env.ps1` | 否（只设环境变量） | ✅ 允许 |
| 调用 `.tools/` 脚本（脚本内部 loader 读 `.env.local`） | 否（agent 看不到 value） | ✅ 允许 |
| `$KEY` / `$env:KEY` 展开（用已加载的变量） | 否（展开瞬间于内存） | ✅ 允许 |
| `cat` / `read` / `grep` / `Get-Content` / `type` 读 `.env.local` | **是** | ❌ 禁止 |
| `printenv` / `env` / `set` / `Get-ChildItem Env:` 枚举密钥变量 | **是** | ❌ 禁止 |

关键区分：明文只在「shell 展开瞬间」于内存存在；agent 永远不把明文「打印」进对话上下文。
`source`（设变量、不打印）≠ `cat`（打印明文）。

## 单一真源

- `.env`（**可提交**）：占位符 / 共享默认值（KEY 留空）【模板占位：按你的工具链增删 KEY】。
- `.env.local`（**不进 git**，已 `.gitignore`）：个人真实密钥，覆盖 `.env`。
- **不在 OS 环境变量 / 各工具配置文件里放明文副本**——明文只在 `.env.local` 一处，缩小泄密面。
- 脚本读取优先级（`_env_loader.py`）：`os.environ` 非空值 > `.env.local` > `.env`。

## 各 agent 工具用法（统一走「加载」，不区分工具）

### 交互式：命令里要用密钥时（`$KEY` 展开）

bash（多数 agent 的默认 shell）：

```bash
source .tools/env/load-env.sh          # 设变量到当前 shell，不回显
mysql -h "$MYSQL_HOST" -p"$MYSQL_PASS" # $KEY 展开，明文不进上下文
```

PowerShell：

```powershell
. .\.tools\env\load-env.ps1
mysql -h $env:MYSQL_HOST -p"$env:MYSQL_PASS"
```

### 脚本式：调用 .tools 脚本时（agent 完全不碰 `.env.local`）

脚本内部用 `_env_loader.py` 自动加载，agent 直接调用即可：

```bash
python .tools/<你的脚本>.py --token-required-cmd
```

### 为什么不用各工具的配置级 env 注入

部分工具有配置级 env 字段（如 `.claude/settings.local.json` 的 `env`），部分工具没有——**统一走 source/脚本加载**：能力对齐所有工具，且避免明文在多处配置扩散。

## 脚本侧共享加载器 `.tools/_env_loader.py`（零依赖，纯标准库）

| 函数 | 用途 |
| --- | --- |
| `get(key, default=None, files=...)` | 优先 `os.environ` 非空 > 文件；`files=(".env.local",)` 可限定只读 .env.local |
| `require(key)` | 读不到非空值 `sys.exit(1)`，只提示缺哪个 key（不泄露 value） |
| `load_into_environ(override=False)` | 合并到 `os.environ`（默认 setdefault 不覆盖已有） |
| `as_dict()` | 返回合并后的 `{KEY: value}` dict |

供 `.tools/` 脚本 import，替代各脚本手写解析。

## `.env.local` 格式约束

须为合法 shell 赋值（被 `load-env.sh` 逐行解析）：

```text
KEY=value
KEY="value with spaces"      # 含空格用双引号
KEY='literal$dollar'         # 含 $ / 反引号用单引号防 shell 展开
# 注释行以 # 开头
```

## 安全红线（详见 AGENTS.md「安全红线」）

- 禁 agent 用 `read` / `cat` / `grep` / `Get-Content` / `type` 等**打印类**操作读 `.env.local`（及任何密钥载体）。
- 禁 agent 用 `printenv` / `env` / `set` / `Get-ChildItem Env:` **枚举/查看**已加载的密钥环境变量。
- 允许 `source` / `load-env.*` **加载**（不回显）+ `$KEY` 展开。
- 凭据不外泄（绝对禁令，即使用户主动要求导出也不行）。
