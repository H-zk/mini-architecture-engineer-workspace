---
name: repo-maintenance
description: 仓库维护标准流程。当用户要求同步 src/ 仓库、clone 新仓库、发现活跃仓库、迁移 origin 或仓库对账时加载。覆盖对账/同步/发现/clone/迁移五个独立且显式授权的阶段；工具脚本与内网主机按【模板占位】接入后启用。
updated-at: 2026-08-30
triggers:
  - 仓库同步
  - clone 仓库
  - 发现活跃仓库
  - 仓库对账
  - origin 迁移
---

# repo-maintenance

> 本文是仓库维护标准流程的单一真源。仓库清单真源 = `reference/repos.md`（人类主写、AI 辅助）。
> **无独立状态机**：本 skill 由 `#workspace-optimize` 任务承载（两态 Lifecycle 见 workspace-ops；维护菜单「维护仓库」入口），本文件 frontmatter 不设 `states:`。

**【模板占位】启用前提**：五阶段配套的 `.tools/` 脚本（sync-repos / find-active-repos / clone-active-repos / migrate-origins）未随模板内置——按接入仓群落地脚本后本流程即全部启用；未落地前可手工按阶段协议执行小规模操作（对账 / 同步），发现与批量 clone 阶段以脚本落地为准。

## When（何时触发）

- 定期维护（同步 src/、发现活跃仓库、clone 新仓库）。
- 仓库对账（repos.md ↔ src/ ↔ origin）。
- HTTP→HTTPS origin 迁移。

## 五个独立阶段（每阶段独立授权）

| 阶段 | 工具 | 授权 |
| ---- | ---- | ---- |
| ① 对账（只读） | `sync-repos.py`（无参 / `--check-only`） | 默认允许 |
| ② 同步 | `sync-repos.py --apply` | 任务级网络授权 |
| ③ 发现 | `find-active-repos.py` | 【模板占位：内部代码托管平台 API 只读授权】 |
| ④ clone | `clone-active-repos.py --plan --expected-sha256 --approve` | 消费已审核计划 |
| ⑤ 迁移 | `migrate-origins.py --verify/--apply-md/--apply-origin` | 清单写入 + origin 修改授权 |

clone/fetch 既有授权**不**扩张为代码托管平台 API、客户环境或生产访问授权。

## Steps

### ① 对账（默认只读）

```bash
python .tools/sync-repos.py                # dry-run：对账 + pull 计划
python .tools/sync-repos.py --check-only   # 只对账
```

报告：repos.md 有但 src/ 没有（待 clone）、src/ 有但 repos.md 没记录（待补录）、origin 不一致。

### ② 同步

```bash
python .tools/sync-repos.py --apply
```

协议：**预检全有或全无** → ls-remote 确认远端默认分支 → fetch → merge --ff-only。移除 stash/reset/pull。dirty/detached/错分支/origin 异常阻断整批。运行期失败停止后续不回滚，幂等重跑。

### ③ 发现

```bash
python .tools/find-active-repos.py > temp/active-plan.json
```

输出 JSON 计划 + SHA-256（committed_date）。**last_activity_at 不作 clone 决策**。

**clone 范围分类**（生成摘要与人审计划时的参考；分类标准与具体清单**以 `reference/repos.md` 标签为准**，不在本 skill 内维护名单）：

- **建议跳过**：对外站点类（官网/文档中心等）与定制/品牌系列（外部定制标签及品牌命名空间）——定制项目的产物服务于该客户、非核心链路，**优先于**前端 SDK 类通配。
- **默认拉**（核心业务）：【模板占位：按你的业务域填写核心仓群分类，如后端微服务 / 核心前端 / SDK】。
- **两类之外**：列入「待勾选」，人审时逐个确认。

### ④ clone

```bash
python .tools/clone-active-repos.py \
  --plan temp/active-plan.json \
  --expected-sha256 <sha> \
  --approve <path1> <path2>
```

固定 target commit；全部先进 `temp/repo-clone-staging/<run-id>/`，验证后逐仓原子 rename 发布。SHA/批准/登记/URL 任一不匹配 → 整批零 clone。

### ⑤ HTTP→HTTPS 迁移

```bash
python .tools/migrate-origins.py --verify          # 只读验证 HTTPS 可达
python .tools/migrate-origins.py --apply-md        # 改 repos.md（需 verify 全通过）
python .tools/migrate-origins.py --apply-origin    # 本地 origin set-url（仅 clean）
```

## Gates

- 日常 clone/sync 只接受【模板占位：你的 git 主机 URL，如 `https://git.example.com/<namespace>/<repo>.git`】；禁止 HTTP/URL 用户名密码/query/fragment/异主机。
- 未登记仓库只能进候选计划，必须先完成 repos.md 登记并验证，才能再获 clone 写入授权。
- `src/.worktrees/` **永不**进入批量同步/clone 目标。
- `has_local_changes` 异常时 fail closed，不按 clean 处理。
- 同步采用「预检全有或全无」，但不承诺跨仓库事务回滚；运行期失败不自动回滚已成功项。

## Outputs

- 对账/同步：终端报告（已更新/失败/未执行 + 锁定目标 commit）。
- 发现：`temp/active-plan.json`（JSON）+ 终端 Markdown 摘要 + stderr 的 SHA-256。
- clone：终端报告（已发布/仍暂存/失败）。
- 迁移：终端报告（成功/跳过/失败）。

## Verify

- 同步/迁移后跑 `python .tools/sync-repos.py --check-only`，确认对账无误。
- clone 后跑 `python .tools/workspace-check.py --section repos`，确认无未登记仓库 error——`repos` 分区随五阶段配套脚本落地时同步扩展，**当前模板未内置（未落地前本条跳过，直接执行会 invalid choice 报错）**，见开头【模板占位】启用前提。
- 全程不 commit/push（AI 编辑、人类提交）。

## 失败兜底

- 同步：失败修复后整批幂等重跑；已更新仓库成为 no-op。
- clone：暂存失败产物不自动删除，清理须操作者授权；发布失败保留可恢复状态，不删除已发布仓库。
- 迁移：origin set-url 后 ls-remote 验证失败则回滚 set-url。
