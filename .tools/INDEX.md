# 可执行工具索引（.tools/）

> 本文件是 `.tools/` 的一句话索引（热层）。收录两类：① **工具调用指导**（何时用/怎么用某类工具）；② **可执行脚本/封装**（命名 `<用途>.<ext>`，同目录附说明）。**经验性文字套路（为什么/选型方法论）归 `exps/`**，本目录只放「怎么调」，互引。
> 准入分阶段：前期某动作手动执行 1 次即可脚本化落地，成熟后转保守（≥2 次）。新增/合并/下线后同步更新本文件；治理规则见 [WORKFLOW.md §2/§6](../WORKFLOW.md)。

<!-- 行格式：标题 | 一句话摘要 | 逗号关键词 | <用途>.<ext> -->

| 标题 | 摘要 | 关键词 | 文件 |
| ---- | ---- | ------ | ---- |
| 工作区一致性检查 | 只读检查：版本一致性 + CURRENT schema/状态不变量 + 正式产物（按执行流 skill Outputs）+ 安全（reset/CERT_NONE/明文密钥）+ links 分区（本地链接存在性 + WORKFLOW §N.M 引用有效性，warning 级）+ markdownlint；error/warning 分级，退出码 0/1/2 | workspace-check, 一致性, 校验, lint, links | workspace-check.py |
| 环境变量加载 | 把 `.env`/`.env.local` 变量注入当前 shell（bash `source` / PowerShell `.`）——「加载不读取」密钥约定；配套 README 讲红线 | env, 密钥, 加载, 加载不读取 | env/load-env.sh, env/load-env.ps1 |
| Claude skills 桥 | 重建 `.claude/skills/` → `.agents/skills/` 的 junction（Windows 免管理员；换机/重 clone 后跑一次） | claude, junction, skills, 桥 | skill-bridge/link-claude-skills.ps1 |

> `_env_loader.py` 是脚本共享的 env 加载器（`.env.local`/`.env`，零依赖，优先级 os.environ > .env.local > .env），供你自写的 `.tools/` 脚本 import（用法见 `.tools/env/README.md`）；不单独索引。

> 扩展位：维护仓库 / 工单查询 / 日志查询等接入你自己的基础设施后在此登记（思路见 [GUIDE.md](../GUIDE.md) §1.2/§3）；外部 API 类脚本一律强制 TLS + hostname 校验 + 最小 scope PAT + 禁重定向（见 AGENTS.md「工具安全」）。
