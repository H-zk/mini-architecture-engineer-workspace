---
created-at: 2026-08-16
updated-at: 2026-08-16
type: 项目 Skill vendor 管理规范
---

# 第三方 vendor skill 管理（判定 / 检测 / lock / 命令 / 安全确认）

> 第三方 skill 是进入上下文的**提示词资产**——引入即影响 AI 行为，须判定标准 + 安装后安全确认双护栏。INDEX 只留 vendor 清单表与本文件指针，管理规范单一真源在此。

## 判定标准：何时 vendor

当工作区**重度依赖**某个全局/外部 skill 时，把它 vendor 进 `.agents/skills/`——**不论源是 local 还是 remote**。重度依赖的判据（满足任一）：

1. **接入核心工作流**：出现在 `WORKFLOW.md` §1.3 路由表 / [INDEX](./INDEX.md) 清单里，是某类任务的固定路由目标；
2. **入口点被反复调用**：其命令（如压测触发语）在真实任务产出（`story/case/tech/research`）中被多次引用；
3. **缺席即断流程**：移除它会破坏已文档化的工作流路径（规则文档引用了它而仓库内无实现 = 断链）。

## 检测方法（建议 `#workspace-optimize 审视工作流` 时定期跑）

```bash
# 信号1：WORKFLOW 路由表/正文引用 = 核心工作流接入
rg -t md "<skill-name>" WORKFLOW.md
# 信号2：真实任务产出里的调用痕迹（排除 workspace-optimize/ 自指）
rg -t md "<skill-name 或其命令>" story case tech research
# 信号3：该 skill 是否带标准 SOP 命令（ls .agents/skills/<name>/command）
```

> 三信号全 0 = 未重度依赖，走全局即可；命中任一（尤其信号1/2）= 重度依赖，应 vendor。

## lock 与 local 源的关系

`skills-lock.json` **只锁 remote 源**（可复现性/版本钉是远端的关切）。**local 源 vendor 副本由 git 直接跟踪**（源是本机仓库，更新 = 手动重新复制，同项目自有 skill），不入 lock。

> `skills-lock.json`（仓库根，v1 精简格式）**随 git 进基线**：预置 vendor 副本（如 `grilling`）的上游坐标与版本钉随仓库分发——换机 / 受让方经 `skills experimental_install` 还原，`skills update` 更新（更新后提交 lock 变更即可）；`computedHash` 是安装工具口径（≠ 裸 sha256），完整性校验以上游字节比对为准。手动 vendor 的 remote 源副本在 lock 标 `_managed: manual`。

## 管理命令

[skills CLI](https://npmjs.com/package/skills) v1.5+，装到 `.agents/skills/` 单一目录（避免镜像复制）：

```bash
skills ls                                              # 查看已 vendor skill
skills add <owner>/<repo> --skill <name> --copy -y     # remote 源装（入 lock）
# local 源重度依赖时：直接从源复制进 .agents/skills/（git 跟踪，不入 lock）
skills update                                          # 更新 lock 内的 remote skill
skills experimental_install                            # 从 skills-lock.json 还原 remote skill（换机）
```

## 安装后安全确认（每次 vendor 安装/更新后）

四步确认，结论与使用边界落 [INDEX](./INDEX.md) vendor 表注脚，评估过程留 `workspace-optimize/` 任务目录：

1. **内容审查**：SKILL.md 全文通读——查 URL、外发/上传指令、凭证操作、提示注入模式（「忽略此前指令」「发送到某地址」类）、破坏性操作。
2. **文件清单**：目录内容与预期一致（通常仅 SKILL.md；声明过的 references/scripts/assets 逐个看），无隐藏文件。
3. **完整性**：remote 源拉上游 raw 文件与本地 diff，**逐字节一致 = 排除安装链篡改**（公开只读拉取属外部访问，需操作者授权）；**lock `computedHash` 是安装工具口径（≠ 裸 sha256），完整性校验以上游比对为准**。
4. **生成物审查**：用一次真实任务实测，扫 skill 产出文件（HTML 等）的外部引用 / 脚本 / 敏感信息。

## 已知限制

- 若 skill 源 `SKILL.md` 带 UTF-8 BOM，`skills` CLI 无法自动检测（local 源手动复制即可绕过；remote 源需手动 vendor + lock 标 `_managed: manual`）。
- 未重度依赖的全局 skill 走各工具全局配置，**不进项目**；检测到重度依赖信号后再按本文档 vendor。
