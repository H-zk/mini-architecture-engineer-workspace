---
created-at: 2026-08-29
updated-at: 2026-08-29
type: worktree 工作区配置资产目录（单一真源；生成器 = .tools/sync-worktree-workspace.py）
---

# workspace-code-setting（code-workspace 配置真源）

> 本目录是「多任务 worktree × 每任务独立 code-workspace」的**配置资产单一真源**，生成器 [`.tools/sync-worktree-workspace.py`](../.tools/sync-worktree-workspace.py) 消费以下资产，为单个任务生成独立 `dev-<task>.code-workspace`（零触碰 review，机器本地不进 git）+ 任务着陆卡 `AGENTS.md`（随任务文档进 git）。
> **改本目录即全局生效**：对已有任务重跑生成器刷新；改完可用生成器 `--check` 检测落后任务。

## 资产清单

| 资产 | 用途 |
| ---- | ---- |
| `setting-example.json` | `.code-workspace` 标准模板：settings 原样下发（骨架：git 隔离三键 + exclude 收口 + 格式化不预置），folders 由生成器按任务 worktree 实时生成（不以此为准） |
| `landing-card.md` | 着陆卡模板（任务目录 `AGENTS.md`）：脚本只做 `{story}`/`{flow_name}`/`{flow_rules}` 占位替换，**模板不嵌脚本、脚本不嵌文案** |
| `git-flows.yaml` | git flow 定义真源（default + flows 字典；每条四要素 name / description / remote_feature / review_gate + card_rules）。各仓用哪条 flow 的登记表见 [reference/branch-flows.md](../reference/branch-flows.md) |
| `code-workspace-env/` | env 铺装：各项目本地开发所需、**不进 git 的环境文件**按仓库存放，README 内映射 `<仓库名> => <worktree 内相对路径>`，生成时铺装到各 worktree（目标已存在同名文件跳过不覆盖） |

## 设计约定

- **模板-数据分离**：生成器只做占位替换，脚本不内嵌文案——改着陆卡文案只改 `landing-card.md`，新增 flow 只在 yaml 加条目，均无需改脚本。
- **模板集版本戳**：生成器写 `.code-workspace` 时计算本目录全部文件的模板集 hash 存入 `_templateHash` 字段（VS Code 忽略未知字段）——`--check` 据此检出落后任务，防模板漂移无声。
- **分层刷新**：`--all` 全量重生成（模板/settings 变更后）；`--card-only` 只补/刷新着陆卡（保护手工雕琢过 folder/settings 的存量工作区）。
- **职责切分**：行为规范真源 = `AGENTS.md` / `WORKFLOW.md`，本目录只管工作区配置。
- 依赖：Python 3.8+；可选 `pyyaml`（缺失时 flow 校验与 card_rules 渲染降级为提示文本，其余功能正常）。

## 常用命令

```bash
python .tools/sync-worktree-workspace.py --task <id> --story <任务目录名>            # 生成/刷新单任务（code-workspace + 着陆卡 + env）
python .tools/sync-worktree-workspace.py --task <id> --story <目录> --card-only     # 只补着陆卡
python .tools/sync-worktree-workspace.py --task <id> --story <目录> --flow mr-review # 显式选 flow
python .tools/sync-worktree-workspace.py --all                                      # 批量刷新已生成工作区的任务
python .tools/sync-worktree-workspace.py --check                                    # 模板状态检测（落后提示）
```

> provenance：目录机制基于 v1 sprint-20260827 提炼（tag c199e14），适配本区五类任务根目录与中性 settings；landing-card 正文沿用本区 reference 早期落地版本。
