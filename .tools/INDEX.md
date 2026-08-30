# 可执行工具索引（.tools/）

> 本文件是 `.tools/` 的一句话索引（热层）。收录两类：① **工具调用指导**（何时用/怎么用某类工具）；② **可执行脚本/封装**（命名 `<用途>.<ext>`，同目录附说明）。**经验性文字套路（为什么/选型方法论）归 `exps/`**，本目录只放「怎么调」，互引。
> 准入分阶段：前期某动作手动执行 1 次即可脚本化落地，成熟后转保守（≥2 次）。新增/合并/下线后同步更新本文件；治理规则见 [WORKFLOW.md §2/§6](../WORKFLOW.md)。

<!-- 行格式：标题 | 一句话摘要 | 逗号关键词 | <用途>.<ext> -->

| 标题 | 摘要 | 关键词 | 文件 |
| ---- | ---- | ------ | ---- |
| 工作区一致性检查 | 只读检查：版本一致性 + CURRENT schema/状态不变量 + 正文软上限 + feat next 受控菜单 token 级校验 + 正式产物 + INDEX 对齐 + 安全 + links + 协议复写 + plainness 平实度（warning）+ coverage 孤儿检测 + markdownlint（error，范围含 `.agents/skills`、vendor 豁免）；error/warning 分级、退出码 0/1/2；支持 `--task` 单任务 / `--staged` 暂存集聚焦；`_tests/` 单元测试（`cd .tools` 后 `python -m unittest discover -s _tests -t .`）；分区细节真源 = 脚本各分区注释 | workspace-check, 一致性, 校验, lint, links, plainness, staged, registration, next, 菜单 | workspace-check.py, _tests/ |
| 会话上下文占用探针 | 只读抽 ZCode 主会话 rollout 流水的 usage 字段，报真实上下文占用 + 逐调用增长轨迹 + `--breakdown` 底座归因粗估（system/工具/消息）；只抽 usage 不打印会话正文（--breakdown 体积估算需按消息体计数，内容不外显）；rollout 路径变动报错即修 | 上下文, context, usage, 探针, rollout | context-usage.py |
| 仓库家族判定 | 只读信号现算各仓「基准分支 + 版本职责」家族视图（构建文件/分支形态/新近度竞速/monorepo 版本），重跑 diff = 家族漂移检测；信号正则为【模板占位】，按接入仓群重配后生效；`--json` 机器可读供 feat 任务消费 | 仓库, 家族, 基准分支, 版本, 漂移 | repo-family.py |
| 工作区活动统计 | 本仓 git log 统计（总提交/时间跨度/逐月/顶层目录 top10，stdlib 零依赖），供阶段回顾与协作节奏复盘复算；`--write` 落 temp/ | 活动, 统计, git log, 回顾 | workspace_activity.py |
| 任务工作区生成器 | 为任务 worktree 生成独立 `dev-<task>.code-workspace` + 着陆卡 AGENTS.md + env 铺装（模板真源 `workspace-code-setting/`，模板集 hash 版本戳：`--check` 检落后 / `--all` 批刷 / `--card-only` 只补卡；`--story` 五类任务根自动定位；flow 定义 `git-flows.yaml`，可选依赖 pyyaml） | worktree, code-workspace, 着陆卡, 生成器, templateHash | sync-worktree-workspace.py |
| codegraph 使用指导 | 代码符号知识图谱工具何时用/怎么调（符号检索/调用关系/影响面；只对代码库，markdown 知识库检索用 ripgrep） | codegraph, 符号, 调用链, 影响面 | codegraph.md |
| ripgrep 使用指导 | rg 何时用/怎么调 + 普查坑（默认静默跳过 .gitignore 忽略与隐藏目录，普查必加 `--no-ignore` / `-uu`） | rg, ripgrep, 搜索, 普查, no-ignore | ripgrep.md |
| 环境变量加载 | 把 `.env`/`.env.local` 变量注入当前 shell（bash `source` / PowerShell `.`）——「加载不读取」密钥约定；配套 README 讲红线 | env, 密钥, 加载, 加载不读取 | env/load-env.sh, env/load-env.ps1 |
| Claude skills 桥 | 重建 `.claude/skills/` → `.agents/skills/` 链接（Windows junction 免管理员 / macOS·Linux symlink；幂等，换机/重 clone 后跑一次） | claude, junction, symlink, skills, 桥 | skill-bridge/link-claude-skills.ps1, skill-bridge/link-claude-skills.sh |

> `_env_loader.py` 是脚本共享的 env 加载器（`.env.local`/`.env`，零依赖，优先级 os.environ > .env.local > .env），供你自写的 `.tools/` 脚本 import（用法见 `.tools/env/README.md`）；不单独索引。

> 扩展位：工单查询 / 日志查询等接入你自己的基础设施后在此登记（思路见 [GUIDE.md](../GUIDE.md) §3；「维护仓库」已由 repo-maintenance skill 兑现内置）；外部 API 类脚本一律强制 TLS + hostname 校验 + 最小 scope PAT + 禁重定向（见 AGENTS.md「工具安全」）。
