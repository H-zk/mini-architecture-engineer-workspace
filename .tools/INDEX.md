# 可执行工具索引（.tools/）

> 本文件是 `.tools/` 的一句话索引（热层）。收录两类：① **工具调用指导**（何时用/怎么用某类工具）；② **可执行脚本/封装**（命名 `<用途>.<ext>`，同目录附说明）。**经验性文字套路（为什么/选型方法论）归 `exps/`**，本目录只放「怎么调」，互引。
> 准入分阶段：前期某动作手动执行 1 次即可脚本化落地，成熟后转保守（≥2 次）。新增/合并/下线后同步更新本文件；治理规则见 [WORKFLOW.md §2/§6](../WORKFLOW.md)。

<!-- 行格式：标题 | 一句话摘要 | 逗号关键词 | <用途>.<ext> -->

| 标题 | 摘要 | 关键词 | 文件 |
| ---- | ---- | ------ | ---- |
| 工作区一致性检查 | 只读检查：版本一致性 + CURRENT schema/状态不变量 + 正文软上限 + feat next 受控菜单 token 级校验 + 正式产物 + INDEX 对齐 + 安全 + links + 协议复写 + plainness 平实度（warning）+ coverage 孤儿检测 + markdownlint（error，范围含 `.agents/skills`、vendor 豁免）；error/warning 分级、退出码 0/1/2；支持 `--task` 单任务 / `--staged` 暂存集聚焦；`_tests/` 单元测试（`cd .tools` 后 `python -m unittest discover -s _tests -t .`）；分区细节真源 = 脚本各分区注释 | workspace-check, 一致性, 校验, lint, links, plainness, staged, registration, next, 菜单 | workspace-check.py, _tests/ |
| 平实度词表 | 字词级 AI 味检测与修复共享数据件（非会话注入）：使用协议（事实保护优先/双模式/分级处置/语域两档/发送前自检）+ 中文主词表十五类 + 结构层四判据 + 英文附录；消费方 = plainness-check skill（编排层）与 workspace-check plainness 分区（词表字词级机检联动后批接入）；上游演进经 skill 市场巡检拉 diff 重吸收 | plainness, 词表, AI味, 平实度, lexicon, 语域, 盲检 | plainness-lexicon.md |
| ZCode 会话原文提取器 | 抽 `~/.zcode/cli/rollout/` model-io 流水的**对话正文**出 Markdown 转录（与 context-usage 同数据源不同动作：它抽 usage 不读正文，本工具读正文）：`--latest` 最新主会话 / `--rollout <路径>` / `--list`（subAgent 文件独立分文件，标注识别）；按 messageOffset 跨记录窗拼接去重，链式分纪元（上下文压缩 offset 归零开新链、同 offset 内容冲突判外来流不并链）；消息分类 user-real（剥 system-reminder）/ assistant（文本 + 工具调用注记）/ injected / tool-result（后两类默认略，旗标含）；`--out <md>` 出转录（头部自带覆盖边界声明——滚动窗口外早期轮次不可恢复，以 commit/任务档案补证）；**自评/会话评审的一手证据源**（任务台账系被评审方自写，只作导航不作证据）；转录含会话原文勿外传 | 会话, 原文, 转录, rollout, 自评, 证据, 评审, messageOffset, 压缩, 纪元, 链, 一手证据 | rollout-extract.py |
| HTML 渲染验收 | 通用引擎：CDP 连本地 Chrome（默认 9222）→ 逐元素几何审计（尺寸/内容溢出/`--max-h` 超限，退出码 0/1）+ 可选 `--pdf` printToPDF 成品、`--shots <dir>` 逐元素截图（`captureBeyondViewport` 绝对裁剪）、`--eval` 自定义探针；零 npm 依赖（Node ≥22——fetch 18+ 可用、全局 WebSocket 客户端 22 起默认），Chrome 需先带 `--remote-debugging-port` 启动 | html, 渲染, 验收, cdp, 截图, printtopdf, 溢出, 几何, 审计 | html-render-audit.mjs |
| 机检在册豁免台账 | workspace-check warning 分诊真源：表行（组前缀 / 文件〔`*`=全组〕/ 理由 / 复核期）命中即移入「在册豁免」分桶——warnings 只数待办、明细不刷屏；豁免 = 有归属有理由有复核期的知情在册，复核期到点未消化即处置台账行；机检消费（warnreg 分区）后批接入、接入前为人工分诊台账 | warning, 豁免, 台账, 分诊, 在册, warnings-registry, workspace-check, 待办池 | warnings-registry.md |
| exps 错误驱动检索 | 错误驱动召回发现引擎（WORKFLOW §2.4）：命令失败/异常输出先拿特征词查 exps/INDEX.md 热层（标题/摘要/关键词/场景列；特征 = 错误码/引号串/包名/实词/CJK 词）再深查根因——命中即用 + 记 TRIGGERS 疑似候选，零命中 = INDEX 缺词信号（先查 notes/INDEX.md 兜底）；`--scene` 过滤、`--file -` 读 stdin、`--self-test` 真值对数 + 解析统计自检（撕裂行漏检/粘连行错位运行时提示）；只读零依赖 | exps, 检索, 错误, 召回, 再犯, 命中, 缺词, 场景, 台账, triggers, 解析自检 | exp-lookup.py |
| 会话上下文占用探针 | 只读抽 ZCode 主会话 rollout 流水的 usage 字段，报真实上下文占用 + 逐调用增长轨迹 + `--breakdown` 底座归因粗估（system/工具/消息）；只抽 usage 不打印会话正文（--breakdown 体积估算需按消息体计数，内容不外显）；rollout 路径变动报错即修 | 上下文, context, usage, 探针, rollout | context-usage.py |
| 仓库家族判定 | 只读信号现算各仓「基准分支 + 版本职责」家族视图（构建文件/分支形态/新近度竞速/monorepo 版本），重跑 diff = 家族漂移检测；信号正则为【模板占位】，按接入仓群重配后生效；`--json` 机器可读供 feat 任务消费 | 仓库, 家族, 基准分支, 版本, 漂移 | repo-family.py |
| 工作区活动统计 | 本仓 git log 统计（总提交/时间跨度/逐月/顶层目录 top10，stdlib 零依赖），供阶段回顾与协作节奏复盘复算；`--write` 落 temp/ | 活动, 统计, git log, 回顾 | workspace_activity.py |
| 任务工作区生成器 | 为任务 worktree 生成独立 `dev-<task>.code-workspace` + 着陆卡 AGENTS.md + env 铺装（模板真源 `workspace-code-setting/`，模板集 hash 版本戳：`--check` 检落后 / `--all` 批刷 / `--card-only` 只补卡；`--story` 五类任务根自动定位；flow 定义 `git-flows.yaml`，可选依赖 pyyaml） | worktree, code-workspace, 着陆卡, 生成器, templateHash | sync-worktree-workspace.py |
| codegraph 使用指导 | 代码符号知识图谱工具何时用/怎么调（符号检索/调用关系/影响面；只对代码库，markdown 知识库检索用 ripgrep） | codegraph, 符号, 调用链, 影响面 | codegraph.md |
| graphify 使用指导 | 全语料知识图谱（god-nodes/社团/graph.html 可视化）= **全景调研按需件**（主战场 codegraph 占优，同场对照）；uvx 按需消费（`graphifyy@0.9.67`）+ 建图驱动 graphify/build.py（uv 工程）；红线 = 禁 install（写 agent 配置）、语义层默认不启用 | graphify, 全景, 知识图谱, 社团, god-nodes, 可视化, uvx, 全景调研 | graphify.md |
| graphify 建图驱动 | 初建流水线固化（detect → AST 零 LLM → 合并 → 建图聚类报告），uv 隔离工程（pyproject + uv.lock，`graphifyy==0.9.67` 钉死）：`uv run --project .tools/graphify python .tools/graphify/build.py <仓根>`，产物落 `<仓根>/graphify-out/`；查询面走 graphify CLI，坑见 graphify.md | graphify, 建图, 驱动, 流水线, uv, graphify-out | graphify/build.py |
| src 仓统一 git 忽略铺装 | 源仓工具产物的统一本地忽略（`.codegraph/` + `graphify-out/`）：真源 `src-git-excludes.txt` + 幂等铺装器把托管块写进 src/ 全部仓（`.worktrees/` 不动）的 `.git/info/exclude`——与全局/XDG ignore 叠加生效、不写 core.excludesFile（避免遮蔽）；新 clone 仓后重跑一次；改忽略项只改真源文件 | git, ignore, excludes, codegraph, graphify, 源仓, 本地忽略, 铺装, 幂等 | apply-src-git-excludes.py, src-git-excludes.txt |
| ripgrep 使用指导 | rg 何时用/怎么调 + 普查坑（默认静默跳过 .gitignore 忽略与隐藏目录，普查必加 `--no-ignore` / `-uu`） | rg, ripgrep, 搜索, 普查, no-ignore | ripgrep.md |
| 环境变量加载 | 把 `.env`/`.env.local` 变量注入当前 shell（bash `source` / PowerShell `.`）——「加载不读取」密钥约定；配套 README 讲红线 | env, 密钥, 加载, 加载不读取 | env/load-env.sh, env/load-env.ps1 |
| Claude skills 桥 | 重建 `.claude/skills/` → `.agents/skills/` 链接（Windows junction 免管理员 / macOS·Linux symlink；幂等，换机/重 clone 后跑一次） | claude, junction, symlink, skills, 桥 | skill-bridge/link-claude-skills.ps1, skill-bridge/link-claude-skills.sh |

> `_env_loader.py` 是脚本共享的 env 加载器（`.env.local`/`.env`，零依赖，优先级 os.environ > .env.local > .env），供你自写的 `.tools/` 脚本 import（用法见 `.tools/env/README.md`）；不单独索引。

> 扩展位：工单查询 / 日志查询等接入你自己的基础设施后在此登记（思路见 [GUIDE.md](../GUIDE.md) §3；「维护仓库」已由 repo-maintenance skill 兑现内置）；外部 API 类脚本一律强制 TLS + hostname 校验 + 最小 scope PAT + 禁重定向（见 AGENTS.md「工具安全」）。
