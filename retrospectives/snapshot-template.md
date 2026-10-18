---
created-at: 2026-08-29
updated-at: 2026-10-18
type: 工作区分层快照模板（迭代边界状态锚；对照材料，不改定位基准）
---

# snapshot-template｜工作区分层快照模板

> 阶段回顾的配套分层快照产物（template 线随按需回顾），落 `position/snapshots/snapshot-sprint-<YYYYMMDD>.md`（结构契约自足；实例由受让方首个迭代回顾产出）。**结构固定**（下述章节顺序与标题不增删、不重排）——这是相邻快照可比的前提，章节级 diff 即版本差异信号；配合 frontmatter 的 from/to-commit 与 `git log --oneline <from>..<to>` 即双通道版本差异分析。

## frontmatter 四锚（复制后填齐）

```yaml
---
created-at: <YYYY-MM-DD>
updated-at: <YYYY-MM-DD>
type: 工作区分层快照（迭代边界状态锚；对照材料，不改定位基准）
sprint-version: <YYYYMMDD>
tag: sprint-<YYYYMMDD>（<hash；独立发起未打 tag 时记「未打」>）
from-commit: <上次回顾 to-commit>
to-commit: <本次回顾 HEAD>
---
```

## 正文章节契约（顺序固定，不增删不重排）

```markdown
# snapshot-sprint-<YYYYMMDD>｜工作区分层快照

## TL;DR

<3-5 句：本期定位一句话 + 关键比例（治理:业务）+ 在途量 + 热区/最大变化>

## 一、七层全景模型

<mermaid 层叠图：定位层→顶层文档层→能力层→任务层→知识层→代码层→治理冷层，含「机制反哺」回边；结构照样例，仅数据更新>

## 二、定位层（position/）

<定位/形态判据有无变化；对比体系动态（对象数、本期新增对比报告）；基准是否被触碰>

## 三、顶层文档层

<真源文档表：角色 + 本期变更（WORKFLOW version、ARCHITECTURE 评分快照、BACKLOG 编号推进、CHANGELOG 条目数）>

## 四、能力层

<skill/commands/tools 计数与本期增删；触发通道变化；安全基座动态>

## 五、任务层

<各根目录任务量表（活跃/归档/在途）+ 在途面板表（任务/状态/一句话目标/卡点）+ Lifecycle 机制本期变化>

## 六、知识层

<exps/notes/reference 计数与本期增量；毕业情况；可靠性分层有无例外>

## 七、代码层

<src namespace 与克隆数、在途 worktree 清单、git flow 使用动态>

## 八、治理冷层

<回顾/ grill / 成长分析本期动作；BACKLOG 信号行新增；成熟度收口结果（定型/试行/退役）>

## 九、数据画像

<当期计数总表，行列结构与样例保持一致，便于跨期 diff>

## 十、诊断与观察

<3-4 条：飞轮健康度 / 结构性张力（治理:业务）/ 本期异常信号 / 下期观察点>

## 附录：计数口径

<计数来源与方法（同口径才可比）；采集方式；安全声明（未触碰密钥文件）>

## 变更历史

- <YYYY-MM-DD 首次生成（承接 retro-<YYYY-MM-DD>.md）>
```
