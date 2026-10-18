---
created-at: 2026-10-18
updated-at: 2026-10-18
type: workspace-review 提交拆分技法（全暂存起点 / 临时编辑法脚本化前必读）
---

# 提交拆分技法（commit-splitting）

> 与 SKILL.md 步骤 6 的分工：未暂存起点的补丁法 / 临时编辑法真源在 SKILL 正文；本件承载**全暂存起点两法 + 手术对账纪律 + 脚本化防御结构**。

## 1. 起点分流判据（先选路再动手）

| 起点 / 授权形态 | 手法 |
| ---- | ---- |
| 整批已暂存，或授权不含索引操作（AGENTS「暂存区边界」） | **pathspec 提交法**（零索引操作） |
| 操作者明确授权 `git add` / `git reset` | **分组 add 法**（最直接） |
| 改动未暂存 | SKILL.md 步骤 6 补丁法 / 临时编辑法 |

## 2. 全暂存起点两法

### pathspec 提交法（零索引操作）

`git commit -F <msgfile> -- <路径列表>`：按**工作树内容**提交指定路径，其余暂存内容原样留在索引里等后续 commit——全程零 `git add` / `git restore --staged`。配套四动作：

1. 基线锚点：`git rev-parse HEAD` 记录拆分前基线（收尾对账用）；
2. 混合文件手术（临时编辑法变体）：`cp` 备份终态 → 编辑到中间态（只含截至本主题的改动）→ pathspec commit → `cp` 还原终态（供下一主题继续切）；
3. 每 commit 后 `git show --stat HEAD` 核验规模与文件集；
4. 收尾完整性：`git diff --shortstat <基线> HEAD` == 净 diff（文件数 + 增删行）且 `git status` 干净；手术备份（temp）用完即清。

### 分组 add 法（有索引授权时最直接）

`git reset` 全部退回工作树 → 按主题分组 `git add <路径>` → 每组跑 `--staged` 聚焦门禁 → commit → 下一组。

## 3. 手术与对账纪律（实操七坑）

1. **中间态必须累积**：第 N 个 commit 的混合文件状态 = HEAD + 已提交主题 + 本主题。写成「HEAD + 本主题」会**静默回滚**前一 commit 刚提交的内容（后一 commit 的 diff 出现反向删除）。
2. **回退表格行不能凭 diff 目测手打**：表格行带大量对齐填充空格，目测重建字节不精确（实测同量级字符差恒显示为变更）——用 `git show HEAD:<file>` 提取原行精确替换。
3. **行尾保护**：工作树 CRLF / blob LF 混合时，脚本读写一律 `newline=''`，防整文件行尾被改写成大 diff。
4. **pathspec 路径清单禁手列**：手列清单会漏文件——从 `git status --porcelain` / `git diff --cached --name-only` 按主题过滤导出；主题分组在规划层做，执行层路径全集永远以 git 输出为准。漏并文件趁未推送 `git commit --amend --no-edit -- <path>` 并入。
5. **完整性对账口径 = 最终暂存态**：修复轮重新 add 后，Σ对账基线取**最后一次** `git diff --cached --shortstat`（口径漂移会被误读成拆分丢失/多行）。
6. **commit 信息终端乱码先字节级验证**：GBK 控制台下 `git log` 中文乱码 ≠ commit 对象损坏——python `subprocess.run(capture_output=True)` + `.decode('utf-8')` 逐条验证；验证输出禁用 `head -c` / `cut -c`（按字节截断把多字节汉字截半产生伪乱码）。
7. **多 commit 完整性对账脚本化**：numstat 求和替代 shortstat 目测——python 一次算 Σ各 commit（文件数/增/删）与 `git diff <基线> HEAD --numstat` 净值三对账。

## 4. 脚本化防御结构（临时编辑法脚本化前必读）

把临时编辑法脚本化批量执行时的两个事故陷阱，防御式写法一句话可免：

- **陷阱一：`io.open(path, "w")` 先截断、参数后求值**——`open(..., "w")` 在对象创建时即截断文件，之后才求值 `.write()` 参数；参数构造若内部读同一文件，拿到的是截空版。防御 = 先求值成局部变量再开写句柄（读 → 计算 → 写回三步不并一句）。
- **陷阱二：循环副作用写在 try 外**——副作用循环在 try 外抛异常时，finally 的还原逻辑不执行，工作树停半完成中间态、内存备份随进程丢失。防御 = 「读终态 → 求值全部中间态（内存）→ 写 → add → finally 还原」五步，后三步必须同守卫。
- 恢复备忘：截空文件用「会话记录全文 + `git show HEAD:<path>` 尾部」重建（净 diff numstat 对账事故前值即闭环）；中间态文件用还原操作的逆（锚定行插回）恢复。

## 5. 门禁衔接

全暂存状态下 `--staged` 检查的是整个暂存集（超集，一次通过即覆盖全部子集内容），逐 commit 内容核验靠 `git show --stat` + 行级 `git diff HEAD` 抽查兜底；commit 信息确认门禁照走。
