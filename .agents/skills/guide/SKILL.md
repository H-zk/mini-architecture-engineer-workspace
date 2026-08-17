---
name: guide
description: 新手引导（快速适配模板）。拉下仓库后的首次会话由 AGENTS frontmatter onboard-state: 待引导 强制触发（跳过则永久豁免）；当操作者说「新手引导」「快速适配」「带我上手」「处理 GUIDE」、想一次性完成模板适配（业务范围定调 → 环境与仓库 → 占位落填 → 首任务验证），或适配完成后想把 GUIDE 退役（缩为存根 + 清引用）时使用。
updated-at: 2026-08-17
triggers:
  - 新手引导
  - 快速适配
  - 带我上手
  - 处理 GUIDE
  - 首次会话强制触发（onboard-state: 待引导）
---

# guide — 新手引导（快速适配 + 用后退役）

> GUIDE 是一次性新手引导材料：本 skill 带操作者快速把中立模板变成实战工作区（业务范围定调 → 环境与仓库 → 占位落填 → 首任务验证），适配完成后把 GUIDE 缩为退役存根并清理引用。跨会话状态由 AGENTS frontmatter `onboard-state` 承载（待引导 / 已完成 / 已跳过）。

## When（何时触发）

- **首次会话强制触发**：AGENTS frontmatter `onboard-state: 待引导` → 会话开始即走本 skill（闸门规则见 AGENTS「首次会话引导闸门」）；操作者明确跳过 → 置 `已跳过` 永久豁免；
- 新用户想快速把模板变成自己的工作区（不想逐条手读 GUIDE）；
- 适配已完成、想把 GUIDE 退役（缩为存根 + 清引用）；
- 换机 / 新 clone 后重跑（GUIDE 已是存根时按存量状态续走）。

## Steps

1. **状态检测**：`grep -rn "【模板占位" --include="*.md" .`（排除 archive/）对照 GUIDE §4 总表 → 未填落点清单；全填 → 直接进第 7 步（退役段）。
2. **业务范围定调（快速业务化第一问）**：三选一——本工作区服务**某个业务** / 一条**产品线** / **公司全业务**？定调后续一切落填与组织建议：
   - 角色定位措辞（README 首行 + 文档地图）：「XX 业务 XX 工程师」/「XX 产品线 XX」/「公司级 XX」；
   - AGENTS 首段业务领域粒度：单领域 / 多子领域列举 / 公司业务版图概述；
   - `reference/repos.md` 组织：namespace 按仓库 / 按产品 / 按部门，配套标签维度建议；
   - `notes/` 主题结构：按业务 / 按产品 / 按域分主题。
3. **环境与仓库引导**：
   - 环境：提示密钥单一真源 `.env.local`（AI 不读取、不代填，操作者自己编辑，见 `.tools/env/README.md`）；代码托管平台访问建议 **personal access token + 最小 scope（只读）起步**、credential helper 由操作者控制（红线见 AGENTS「安全红线」，规格见「工具安全」）；
   - 仓库：按定调的 namespace 方式起草 `reference/repos.md` 登记行（reference 人类主写——**预览逐条确认后**写入）；问是否当场 clone 进 `src/<namespace>/<repo>/`（clone 即授权 AI 工作）；提示分支约定可落 `reference/`（AGENTS「代码视图隔离」占位）。
4. **剩余占位批量问答**：一次问齐——工作区角色定位与业务领域（按定调措辞）、工单/项目管理系统名（WORKFLOW §2.7）、首个迭代号 + 周期（retrospectives 节点锚，可跳过）、case 问题来源占位（工单 / 消息群等按实际渠道）——给出**落填预览**（文件 × 位置 × 新值），操作者确认后一次写入；`HUMAN.md` 的改动（§0.3 表）单独逐条确认（人类主写）。
5. **任务接入走查**：按 GUIDE §2 五类顺序（tech → research → case → feat → workspace-optimize）逐类给接入建议，只展开操作者关心的；引导发首个 `#tech` 真问题。
6. **验证（适配完成判据）**：`python .tools/workspace-check.py` 全量 `errors=0` + `#tech` 跑通产出 `answer.md` → **置 AGENTS frontmatter `onboard-state: 已完成`**。
7. **退役段（操作者确认后执行）**：
   - GUIDE 缩为 ≤5 行存根：适配完成日期 + 一句「新手内容已消费完，日常入口如下」+ 指向 [README](../../../README.md)（入口与心智模型）/ [HUMAN](../../../HUMAN.md)（操作 SOP）/ skills [INDEX](../INDEX.md)（能力清单）；
   - 清理 § 锚引用：`grep -rn "GUIDE" --include="*.md"` 的存活命中里，指向 GUIDE § 小节的改为自包含表述或改指 HUMAN / skills INDEX（语义改写、不逐字节登记）；
   - 退役门禁：`grep "GUIDE"` 仅剩存根自身与历史层（archive/、CHANGELOG、任务目录）命中 + 全量 workspace-check `errors=0`；
   - **可选连带退役本 skill**：操作者确认后删除 `guide/` 目录与 `.agents/commands/guide.md` 并清 skills INDEX 对应行（新手引导用完即走；删除用绝对路径）。

**跳过处理（任意环节操作者明确说跳过整体引导）**：置 AGENTS frontmatter `onboard-state: 已跳过`，告知「随时 `/guide` 或说『新手引导』可回来」后正常结束——不算失败，纯任务协作不依赖适配。

## Gates

- 密钥红线：`.env.local` 只加载不读取，**不代填任何密钥**；
- `reference/`、`HUMAN.md` 写入须操作者显式确认（人类主写）；
- `onboard-state` 改写仅两个时点：**明确跳过** → `已跳过`；**验证全过** → `已完成`（中途暂停不改状态，下次会话闸门会再唤起）；
- 退役与 skill 自删均为**先问后动**的确认动作；删除类操作一律绝对路径。

## Outputs

- 落填后的占位（GUIDE §4 总表范围内，措辞按业务范围定调）+ `repos.md` 登记行 + 可选 `src/` 克隆；
- AGENTS `onboard-state` 终态（已完成 / 已跳过）；
- 适配完成（用户仓本地）：GUIDE 退役存根 + 引用清理。

## Verify（DoD）

- 占位清零或明示跳过项；全量 workspace-check `errors=0`；
- `onboard-state` 终态已落盘（已完成 / 已跳过）；
- 退役后 `grep "GUIDE"` 仅存根 + 历史层命中；
- **待首用**：模板主本不真实走引导（防占位落填破坏模板中立），首次真实使用待受让方——首用后按 exps「skill 首跑验证」回写发现。
