---
created-at: 2026-08-29
updated-at: 2026-08-30
type: 分支家族约定与 git flow 登记（AI 判定基准分支的真源）
---

# 分支家族约定与 Git Flow 登记（branch-flows）

> 本文件是 AGENTS「代码视图隔离 · 基准分支判定」的配套真源：AI 为目标仓库判定「开发分支 / 基准分支」时先查本文档登记表，登记缺失或低置信 → 咨询操作者（勿凭猜测）。各仓 flow 条目由**人类确认后落填**（AI 可起草、经授权写入）。
> 通用 flow 定义基于 v1 sprint-20260827 提炼（tag c199e14，其 `git-flows.yaml`「flow 即数据」形态）；本仓 yaml 真源随 `workspace-code-setting/` 引进并由生成器消费（见下节），本文登记表为人工维护的只读镜像。

## Flow 定义（通用两档）

**flow 定义单一真源 = [workspace-code-setting/git-flows.yaml](../workspace-code-setting/git-flows.yaml)**（生成器与着陆卡渲染的消费对象）。每条 flow 四要素：`name` / `remote_feature`（feature 分支是否推远端）/ `review_gate`（合入是否过评审门）/ `card_rules`（任务着陆卡上的分支规则文本，支持 `{task}` 占位）。当前内置：

| flow | remote_feature | review_gate | 一句话 |
| ---- | -------------- | ----------- | ------ |
| **centralized**（默认） | false | false | feature 分支只作本地隔离；ff-only refspec 直推开发分支，禁裸 push |
| **mr-review** | true | true | feature 推远端 + MR/PR + 评审通过后合入（开发分支受保护时） |

> 新增一种 flow = 在 yaml `flows:` 下加条目即可（无需改任何脚本）；本表是 yaml 的只读镜像，以 yaml 为准。

## 各仓分支家族登记表【模板占位：操作者按仓落填】

| 仓库（namespace/repo） | flow | 开发分支（基准分支 = 检出分支 = 合并目标） | 版本/发布分支家族约定（一句话） | 备注 |
| --------------------- | ---- | ---------------------------------------- | ------------------------------ | ---- |
| 【模板占位：如 web/frontend-admin】 | 【centralized / mr-review / 自定义】 | 【如 develop / release-sprint / main】 | 【如「develop 集成 + release-* 发版 + main 稳态」】 | |

## 判定规则（AI 消费口径）

1. 登记表命中 → 按登记的「开发分支」执行（worktree 检出、提交、FF/合并推送全以此为目标线）；
2. 未登记 → 按目标仓远端分支家族形态初判（`develop*` / `release-*` / 版本号分支等多为开发线；`main`/`master` 若受保护则多为合并目标而非直接开发线），**低置信即停，咨询操作者**；
3. 判定结果在首个使用该仓的任务 README「代码上下文表」留痕，并**建议操作者回填本登记表**（一次判定、此后机读）。
