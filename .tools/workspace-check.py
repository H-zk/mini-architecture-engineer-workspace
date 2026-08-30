#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workspace-check.py — 工作区一致性只读检查

默认只检查，不修改任何文件。

退出码：
  0 = 全部通过（可能有 warning）
  1 = 存在必须修复的 error
  2 = 工具自身错误

检查项：
  - 版本一致性（WORKFLOW frontmatter / CHANGELOG 最新）
  - CURRENT.md schema + 状态不变量（状态集从各执行流 skill frontmatter states: 读取，
    per-status next/blocker 与产物档位按类型声明；feat 另有 next 受控菜单 token 级校验
    ——越界/裸冒号 = next 未明确；workspace-optimize 已完成需 review 事件 passed/legacy-exempt；
    正文非空行 >60 软上限告警——CURRENT 只留 digest，过程明细归过程产物）
  - 正式产物存在（按任务类型 + 状态档位；archive 内必须已完成；
    story review.md 到强制档位须含固定分区「## 无法决策点」——内容可空，查分区存在性；
    未完成任务 README 首 H1 须含任务目录名——WORKFLOW §1.2，已完成/archive 豁免）
  - INDEX 对齐（活跃任务目录必须在对应根 INDEX.md 登记，error 级；--task/--staged 同查）
  - Markdown 链接/章节引用有效性（links 分区：本地链接存在性 + WORKFLOW §N.M 引用，warning 级）
  - 协议骨架复写（protocols 分区：通用协议句仅许在 WORKFLOW，skill 内命中或指纹真源失配 → warning）
  - 平实度（plainness 分区：机制文档单行/表格行/散文段/括号嵌套四指标，warning 档）
  - 登记完整性（coverage 分区：顶层目录须在 README/AGENTS 目录表出现、position/ 子目录须在
    position/README 出现——孤儿目录 = warning，防「实体落地而入口真源失同步」）
  - 安全检查（reset --hard / CERT_NONE / 关闭 hostname / 疑似明文密钥）
  - temp 卫生（temp/ 应只留 README.md，其余残留告警；--task 单任务模式同查）
  - worktree 卫生（src/.worktrees/ 孤儿/残留告警；--task 只查该任务 md 引用的组）
  - markdownlint（调 markdownlint-cli2，规则真源 .markdownlint.jsonc；违规进 errors）
  - 登记对源侧一致性（registration 分区：构建剔除对旧串须 verbatim 仍在登记面源文件——
    防登记面编辑后漂移到构建期才拦截；全量必跑 + --staged 触发式聚焦；实现外置
    配套模块、缺席即自动下线——开源产物态无此分区）

warning 类（证据闭环 / 文档漂移 / markdownlint 违规）首版简化或跳过，后续批次完善。

用法：
  python .tools/workspace-check.py
  python .tools/workspace-check.py --section tasks
  python .tools/workspace-check.py --section security
  python .tools/workspace-check.py --section versions
  python .tools/workspace-check.py --section temp
  python .tools/workspace-check.py --section worktrees
  python .tools/workspace-check.py --section skills
  python .tools/workspace-check.py --section markdownlint
  python .tools/workspace-check.py --section registration
  python .tools/workspace-check.py --section links
  python .tools/workspace-check.py --section protocols
  python .tools/workspace-check.py --section plainness
  python .tools/workspace-check.py --task workspace-optimize/task-YYYY-MM-DD-xxx   # 单目录增量（任务收尾聚焦）
  python .tools/workspace-check.py --staged   # 暂存集聚焦（lint-staged 式，commit 前机器门禁：
                                               # 只检查 git diff --cached 的文件，与收尾门禁互补）
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 强制 stdout UTF-8：Windows 中文控制台默认 GBK，无法输出 ⚠/✗/中文告警
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / ".tools"

# 状态集真源下放：各任务根目录映射到对应执行流 skill，从其 frontmatter `states:` 字段
# 读取合法状态集（有序列表，即状态机主链顺序）；本工具不再内维护全局枚举映射。
TASK_SKILL = {
    "workspace-optimize": ".agents/skills/workspace-ops/SKILL.md",
    "story": ".agents/skills/feat-plan-research/SKILL.md",
    "case": ".agents/skills/case-troubleshoot/SKILL.md",
    "tech": ".agents/skills/tech-consult/SKILL.md",
    "research": ".agents/skills/research-survey/SKILL.md",
}

# 历史豁免白名单（模板起点为空；出现「已完成但缺 review 事件」的历史任务时按需登记，仅允许 legacy-exempt）
LEGACY_EXEMPT_TASKS = set()

# 正式产物门禁（per-status 下放，按类型声明；语义见对应 skill Lifecycle / Outputs）：
#   value = 从哪个状态起强制（按 skill states: 声明顺序比较）；None = 全程强制（立项即建）。
#   story：plan.md 从 编码中 起（编码必须有已确认 plan）、review.md 从 审核中 起（交付三件套）；
#   两态标签（case/tech/research/workspace-optimize）正式交付物在 已完成 强制，进行中不强迫。
TASK_REQUIRED = {
    "workspace-optimize": {"README.md": None, "CURRENT.md": None},
    "story": {"README.md": None, "CURRENT.md": None, "plan.md": "编码中", "review.md": "审核中"},
    "case": {"README.md": None, "CURRENT.md": None, "analysis.md": "已完成", "conclusion.md": "已完成"},
    "tech": {"README.md": None, "CURRENT.md": None, "answer.md": "已完成"},
    "research": {"README.md": None, "CURRENT.md": None, "report.md": "已完成", "refs.md": "已完成"},
}

# review.md 固定分区（story 审核中子协议）：产物到
# TASK_REQUIRED 强制档位（review.md 从 审核中 起）时，必须含精确二级标题「## 无法决策点」——
# 分区固定、内容可空（空分区或「无」均合法，查的是分区存在性）；「审核中」入态分支按此机械化
# 分流（真源 feat-plan-research SKILL.md 审核中子协议 / 交付门禁）。仅活跃区生效——archive 不跑
# _check_products，历史任务旧节名（如「待 review 决策点」）保留原貌不校验。
REVIEW_REQUIRED_HEADINGS = {
    "story": {"review.md": "无法决策点"},
}

# per-status next/blocker 规则（随状态机下放，按类型声明）：
#   (next 必填, next 必须为无, blocker 允许非无)。
#   跨类型不变量：已完成 next/blocker 必无；等待语义一律 blocker 字段承载（无「阻塞」态）。
#   feat 审核中例外：等操作者是审核节奏本身、不是卡住 → blocker 必无，next 写当前子步骤
#   （待 grilling / AI 自审轮待触发 / 待操作者终审）；验证中 等发版/等验证环境 = 等外部真卡住 → 允许。
PER_STATUS_RULES = {
    "story": {
        "进行中": (True, False, True),
        "编码中": (True, False, True),
        "审核中": (True, False, False),
        "验证中": (True, False, True),
        "已完成": (False, True, False),
    },
    "case": {"进行中": (True, False, True), "已完成": (False, True, False)},
    "tech": {"进行中": (True, False, True), "已完成": (False, True, False)},
    "research": {"进行中": (True, False, True), "已完成": (False, True, False)},
    "workspace-optimize": {"进行中": (True, False, True), "已完成": (False, True, False)},
}

# feat（story）next 受控菜单（NEXT_MENU，B19 兑现）：token 级校验 = per-status 必填/必无
# 规则的取值细化——无参 token 全字匹配；带参 token（param 集）用 `:` 后缀跟摘要且参数非空
#（裸冒号 = next 未明确）。真源 = feat-plan-research SKILL「next/blocker 约定」节，
# 菜单变更时同步本表；`已完成`（next 必无）由 PER_STATUS_RULES 覆盖、不入本表。
NEXT_MENU = {
    "进行中": ({"待开工", "待确认计划"}, {"实施中"}),
    "编码中": ({"待编码"}, {"实施中", "编码待确认"}),
    "审核中": ({"待 AI 自审", "AI 自审中", "待人类审核", "待授权推送"}, set()),
    "验证中": ({"待发版", "待验收确认"}, {"验证中"}),
}

_STATES_CACHE = {}

# 哪些任务类型的「已完成」需要 review 事件（frontmatter review 字段或正文 review: 行）：
#   workspace-optimize = 完成确认留痕（review: passed，见 workspace-ops skill Lifecycle）。
#   业务标签（story/case/tech/research）不需要——操作者完成确认记 CURRENT 历史正文一句，
#   不写 review: 事件（WORKFLOW §2.6 状态机通用协议第 6 条：review: 事件仅 #workspace-optimize 使用）。
REVIEW_EVENT_REQUIRED = {"workspace-optimize"}


def load_states(task_type):
    """读取该类型执行流 skill frontmatter `states:`（有序状态列表）；缺失/解析失败返回 None。"""
    if task_type in _STATES_CACHE:
        return _STATES_CACHE[task_type]
    states = None
    skill_rel = TASK_SKILL.get(task_type)
    if skill_rel:
        try:
            m = re.search(r"^states:\s*\[([^\]]+)\]", (ROOT / skill_rel).read_text(encoding="utf-8"), re.M)
            if m:
                states = [s.strip() for s in m.group(1).split(",") if s.strip()]
        except Exception:
            states = None
    _STATES_CACHE[task_type] = states
    return states


# ─── 工具函数 ──────────────────────────────────────────────────────

def parse_current(path):
    """解析 CURRENT.md frontmatter。返回 dict（含 _body）或 None。"""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fm = text[3:end].strip()
    out = {}
    for line in fm.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    out["_body"] = text[end + 4:]
    return out


def _is_empty(v):
    return v is None or v == "" or v == "无"


# ─── 版本一致性 ────────────────────────────────────────────────────

def check_versions(errors):
    wf_path = ROOT / "WORKFLOW.md"
    if not wf_path.exists():
        errors.append("版本: WORKFLOW.md 不存在")
        return
    wf = wf_path.read_text(encoding="utf-8")
    m = re.search(r"^version:\s*([\d.]+)", wf, re.M)
    wf_ver = m.group(1) if m else None
    if not wf_ver:
        errors.append("版本: WORKFLOW.md frontmatter 缺 version")

    # 版本锚点：WORKFLOW frontmatter version == CHANGELOG 最新条目版本。
    # CHANGELOG 倒序（最新在上）；从首条往下找第一个能提取版本的条目：
    #   bump 条目 "(vX → vY)" → 取 Y；旧格式 "## v<ver>" → 取 ver；"version 不变" → 跳过
    cl_path = ROOT / "CHANGELOG.md"
    cl_ver = None
    if cl_path.exists():
        for line in cl_path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("## "):
                continue
            m = re.match(r"##\s+v(\d+\.\d+(?:\.\d+)?)", line)
            if m:
                cl_ver = m.group(1)
                break
            m = re.search(r"[(（]v?[\d.]+\s*(?:→|->)\s*v?(\d+\.\d+(?:\.\d+)?)[)）]", line)
            if m:
                cl_ver = m.group(1)
                break

    if wf_ver and cl_ver and wf_ver != cl_ver:
        errors.append(f"版本不一致：WORKFLOW {wf_ver} != CHANGELOG v{cl_ver}")


# ─── Markdown 链接 / 章节引用 ──────────────────────────────

MD_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"```.*?```", re.S)
WF_HEADING_RE = re.compile(r"^#{2,4}\s+(\d+(?:\.\d+)*)\.?\s", re.M)
WF_SEC_RE = re.compile(r"§(\d+(?:\.\d+)*)")
# 跨文件引用 WORKFLOW 章节的两种形态（避免把其他文档自身的 § 误报进来）：
#   [..§N.M..](..WORKFLOW.md) 链接式  /  WORKFLOW §N.M 纯文本式
WF_LINK_SEC_RE = re.compile(r"\[[^\]]*?§(\d+(?:\.\d+)*)[^\]]*\]\([^)]*?WORKFLOW\.md")
WF_TEXT_SEC_RE = re.compile(r"WORKFLOW(?:\.md)?\s*§(\d+(?:\.\d+)*)")
# WORKFLOW 自身 § 自检前先剥离两类非自引用：
#   ① 跨文档前缀引用（HUMAN §2.0 / `ARCHITECTURE.md` §4 等，指向他文档自身章节）
#   ② 自述空缺的叙事区间（「原 §4–§6 编号空缺」是描述不是引用）
CROSS_DOC_SEC_RE = re.compile(
    r"(?:`)?(?:HUMAN|AGENTS|ARCHITECTURE\.md|retrospectives)(?:`)?\s*§[\d.]+"
)
NARRATIVE_RANGE_RE = re.compile(r"原\s*§[\d.]+\s*[–-]\s*§[\d.]+")


def _strip_fences(text):
    """去掉围栏代码块——块内 `](path)` 是示例不是链接，检查会误报。"""
    return FENCE_RE.sub("", text)


# 链接检查覆盖面（根层常驻文档）；skills/exps 由 glob 扩展。--staged 复用同一口径
_LINK_UNIVERSE_ROOT = ("AGENTS.md", "README.md", "HUMAN.md", "WORKFLOW.md", "GUIDE.md")
# § 引用检查覆盖面（exps 含历史叙事不查，防误报）
_SEC_REF_ROOT = ("AGENTS.md", "HUMAN.md", "WORKFLOW.md")


def _wf_valid_secs():
    """WORKFLOW 标题编号集（§ 引用校验基准）；WORKFLOW 不存在返回 None。"""
    wf_path = ROOT / "WORKFLOW.md"
    if not wf_path.exists():
        return None
    wf_body = _strip_fences(wf_path.read_text(encoding="utf-8"))
    return set(WF_HEADING_RE.findall(wf_body))


def _check_links_existence(p, warnings):
    """单文件本地 Markdown 链接存在性（warning 级）。"""
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return
    rel = p.relative_to(ROOT).as_posix()
    body = _strip_fences(text)
    for m in MD_LINK_RE.finditer(body):
        target = m.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        if not (p.parent / path_part).resolve().exists():
            warnings.append(f"链接: {rel} → {target} 目标不存在")


def _check_wf_refs(p, warnings, valid_secs):
    """单文件 WORKFLOW §N.M 引用校验；WORKFLOW 自身 § 全量自检（剥离跨文档前缀/叙事区间）。"""
    try:
        text = _strip_fences(p.read_text(encoding="utf-8"))
    except Exception:
        return
    wf_path = ROOT / "WORKFLOW.md"
    rel = p.relative_to(ROOT).as_posix()
    refs = set()
    if p == wf_path:
        cleaned = NARRATIVE_RANGE_RE.sub("", CROSS_DOC_SEC_RE.sub("", text))
        refs.update(WF_SEC_RE.findall(cleaned))
    else:
        refs.update(WF_LINK_SEC_RE.findall(text))
        refs.update(WF_TEXT_SEC_RE.findall(text))
    for sec in refs:
        if sec not in valid_secs:
            warnings.append(f"章节引用: {rel} 引用 WORKFLOW §{sec} 不存在")


def check_md_links(errors, warnings):
    """活跃文档的本地 Markdown 链接存在性 + WORKFLOW §N.M 引用有效性（warning 级）。

    背景：曾出现 WORKFLOW 内错误相对链接、活跃文档残留已删除章节引用——检查全绿但链接悬空，故补本检查。
    范围：根层常驻文档 + .agents/skills + exps（链接存在性）；
    § 引用只查规则热层与 skill（exps 含历史叙事，如「原 §3–§6 已下沉」，查了会误报）。
    CHANGELOG / 任务目录 / workspace-grills 不扫（历史属性，原貌保留）。
    """
    files = [ROOT / p for p in _LINK_UNIVERSE_ROOT if (ROOT / p).exists()]
    for g in (".agents/skills/**/*.md", "exps/**/*.md"):
        files.extend(ROOT.glob(g))

    valid_secs = _wf_valid_secs()
    if valid_secs is None:
        return
    for p in files:
        _check_links_existence(p, warnings)
    sec_files = [ROOT / p for p in _SEC_REF_ROOT if (ROOT / p).exists()]
    sec_files.extend(ROOT.glob(".agents/skills/**/*.md"))
    for p in sec_files:
        _check_wf_refs(p, warnings, valid_secs)


def check_staged_links(rel_paths, warnings):
    """--staged：全部暂存 Markdown 查本地链接；WORKFLOW §引用仍限规则热层与 skill。"""
    valid_secs = _wf_valid_secs()
    for rel in rel_paths:
        p = ROOT / rel
        if not rel.endswith(".md") or not p.is_file():
            continue
        _check_links_existence(p, warnings)
        if valid_secs is not None and (rel in _SEC_REF_ROOT or rel.startswith(".agents/skills/")):
            _check_wf_refs(p, warnings, valid_secs)


# ─── 协议骨架复写检测（通用协议单一真源 = WORKFLOW）──────────────

# 通用协议骨架句仅许出现在 WORKFLOW.md（§2.6 状态机通用协议等）——skill 内只留
# 「判据 + 摘要括号 + 指针」，不复制骨架（2026-08-15 skills 治理批次确立；背景：
# reopen 协议曾在 3 个 skill 近逐字复写、试行期规则复制 5 份）。指纹刻意取完整
# 长句，与 skill 内合法的摘要括号（如「活跃区硬截止 / 翻回留痕收场」）不冲突；
# 背景是通用协议曾出现多 skill 逐字复写漂移；协议改写后同步本清单（真源句变更 → 下方「指纹失配」另行告警）。
PROTOCOL_FINGERPRINTS = [
    "翻回 + 留痕收场后本会话结束",
    "增补工作**新会话**进行",
    "迭代末回顾归档后硬截止",
    "`sprint-version` 保留立项值不随 reopen 改",
    "`review:` 事件仅 `#workspace-optimize` 使用",
    "沉淀只问新产出",
]


def check_protocols(errors, warnings):
    """skill 出现协议骨架句 / 指纹在真源失配 → warning（应上收 WORKFLOW 或改指针）。"""
    wf_path = ROOT / "WORKFLOW.md"
    wf = wf_path.read_text(encoding="utf-8") if wf_path.exists() else ""
    for fp in PROTOCOL_FINGERPRINTS:
        if fp not in wf:
            warnings.append(f"协议复写: 指纹「{fp}」不在 WORKFLOW.md（协议改写后未同步指纹清单）")
    for p in sorted(ROOT.glob(".agents/skills/**/*.md")):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = p.relative_to(ROOT).as_posix()
        for fp in PROTOCOL_FINGERPRINTS:
            if fp in text:
                warnings.append(
                    f"协议复写: {rel} 含通用协议骨架句「{fp}」"
                    "（真源=WORKFLOW，skill 只留判据+摘要+指针）"
                )


# ─── 任务状态─────────────────────────────────────────────

def check_task_current(task_dir, task_rel, errors, warnings):
    cur = task_dir / "CURRENT.md"
    if not cur.exists():
        errors.append(f"{task_rel}: 缺 CURRENT.md")
        return
    data = parse_current(cur)
    if not data:
        errors.append(f"{task_rel}: CURRENT.md frontmatter 解析失败（需 --- 包裹）")
        return

    # 字段名规范：CURRENT frontmatter 用 updated-at 不用 updated（AGENTS 规定；
    # CURRENT 是 grep 依赖的关键文件，字段名漂移会破坏一致性）
    if "updated" in data and "updated-at" not in data:
        warnings.append(f"{task_rel}: CURRENT frontmatter 字段名 'updated'（应为 'updated-at'）")

    status = data.get("status")
    next_v = data.get("next")
    blocker = data.get("blocker")
    body = data.get("_body", "")

    # 状态集从执行流 skill frontmatter states: 读取（真源下放；archive 任务路径同样以
    # 首段目录定类型，如 story/archive/xxx → story）
    task_type = task_rel.split("/")[0]
    states = load_states(task_type)
    if states is None:
        errors.append(
            f"{task_rel}: 无法从 {TASK_SKILL.get(task_type, '?')} frontmatter 读取 states:"
            "（状态集真源缺失或格式非法，应为 states: [状态A, 状态B, ...]）"
        )
        return
    if status not in states:
        errors.append(
            f"{task_rel}: status 非法 '{status}'（{task_type} 合法状态：{states}，真源=skill frontmatter states:）"
        )
        return

    # per-status next/blocker 规则（随状态机下放，按类型声明，见 PER_STATUS_RULES 注释）
    rule = PER_STATUS_RULES.get(task_type, {}).get(status)
    if rule:
        next_required, next_must_empty, blocker_allowed = rule
        if next_required and _is_empty(next_v):
            errors.append(f"{task_rel}: {status} next 必须非空（下一项明确动作）")
        if next_must_empty and not _is_empty(next_v):
            errors.append(f"{task_rel}: {status} next 必须为无（实际：'{next_v}'）")
        if not blocker_allowed and not _is_empty(blocker):
            errors.append(f"{task_rel}: {status} blocker 必须为无（等待语义进 next/进度正文，见 skill Lifecycle）")

    # feat next 受控菜单 token 级校验（B19）：越界取值按 SKILL 约定视同 next 未明确，error
    if task_type == "story" and status in NEXT_MENU and not _is_empty(next_v):
        fixed, param = NEXT_MENU[status]
        norm = next_v.replace("：", ":")  # 宽容全角冒号（中文输入习惯），统一按半角判
        tok, sep, arg = norm.partition(":")
        if not (norm in fixed or (sep and tok in param and arg.strip())):
            menu_s = " / ".join(
                x for x in ("/".join(sorted(fixed)),
                            "/".join(f"{t}:<摘要>" for t in sorted(param))) if x
            )
            errors.append(
                f"{task_rel}: {status} next 越界 '{next_v}'（本态菜单: {menu_s}；"
                f"带参 token 参数非空——真源 feat-plan-research SKILL「next/blocker 约定」）"
            )

    if status == "已完成" and task_type in REVIEW_EVENT_REQUIRED:
        # review 事件（操作者完成确认留痕）：口径 = passed / legacy-exempt；
        # not-applicable 已下线（统一口径：passed / legacy-exempt）。
        # 仅 workspace-optimize 需要——业务标签（story/case/tech/research）的操作者完成
        # 确认记 CURRENT 历史正文一句，不写 review: 事件（WORKFLOW §2.6 状态机通用协议第 6 条）。
        review_fm = data.get("review", "")
        has_review = bool(re.search(r"(passed|legacy-exempt)", review_fm)) or \
            bool(re.search(r"review:\s*(passed|legacy-exempt)", body))
        if not has_review:
            if task_rel in LEGACY_EXEMPT_TASKS:
                warnings.append(f"{task_rel}: 已完成但无 review 事件（白名单，应补 'review: legacy-exempt'）")
            else:
                errors.append(f"{task_rel}: 已完成但无 review 事件（需 passed）")

    # 正文不应重复 status/next/blocker（CURRENT 正文只保留事件）
    for field in ("status", "next", "blocker"):
        if re.search(rf"\*\*{field}\*\*\s*[：:]", body):
            warnings.append(f"{task_rel}: CURRENT 正文重复 {field}（应在 frontmatter，正文只保留事件）")

    # 正文膨胀软上限（CURRENT = 活状态 digest，WORKFLOW §2.6）：物化过程明细归过程产物
    # （对应执行流 skill 定义，暂无定义时留任务目录过程文档），超限只告警不阻断；
    # archive 历史任务保留原貌不告警
    body_lines = [ln for ln in body.splitlines() if ln.strip()]
    if "/archive/" not in task_rel and len(body_lines) > 60:
        warnings.append(
            f"{task_rel}: CURRENT 正文 {len(body_lines)} 非空行（>60；过程明细应归过程产物，CURRENT 只留 digest）"
        )


def _required_ok(required_from, status, states):
    """产物是否已达强制状态：None=全程强制；否则按 skill states 声明顺序比较。"""
    if required_from is None:
        return True
    try:
        return states.index(status) >= states.index(required_from)
    except ValueError:
        return False


def _check_products(entry, task_rel, task_type, status, errors):
    states = load_states(task_type)
    if states is None or status not in states:
        return  # 状态集缺失/非法已在 schema 校验处报错，不重复
    for f, required_from in TASK_REQUIRED[task_type].items():
        if not _required_ok(required_from, status, states):
            continue
        path = entry / f
        if not path.exists():
            errors.append(f"{task_rel}: {status} 缺正式产物 {f}")
            continue
        if f == "README.md" and status != "已完成":
            # 首个 H1 含任务目录名（WORKFLOW §1.2）：README 全员同名，H1 记目录名才能定位；
            # 剥离围栏代码块（块内示例 H1 不算）；无 H1 同样报错（无处记录目录名）。
            # 边界 = 状态制：活跃区未完成任务一律强制（存量已同步回填）；
            # 已完成（README 冻结，留作回顾基准）与 archive（不跑本函数）豁免；reopen 翻回即恢复强制
            try:
                rtext = path.read_text(encoding="utf-8")
            except Exception:
                rtext = ""
            h1 = re.search(r"^#\s+(.+?)\s*$", _strip_fences(rtext), re.M)
            if not h1:
                errors.append(
                    f"{task_rel}: README 缺 H1 标题（首个 H1 须含任务目录名，WORKFLOW §1.2）"
                )
            elif entry.name not in h1.group(1):
                errors.append(
                    f"{task_rel}: README H1 未含任务目录名 '{entry.name}'（实际 H1：'{h1.group(1)}'；"
                    "README 全员同名，H1 记目录名才能快速定位——WORKFLOW §1.2）"
                )
        # 固定分区校验：产物到强制档位才查（如 story review.md 从 审核中 起）；标题行首行尾
        # 锚定精确匹配（防「### 同名」/正文提及误判），剥离围栏代码块（块内示例不算分区）。
        heading = REVIEW_REQUIRED_HEADINGS.get(task_type, {}).get(f)
        if not heading:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            text = ""
        if not re.search(rf"^##\s+{re.escape(heading)}\s*$", _strip_fences(text), re.M):
            errors.append(
                f"{task_rel}: {status} {f} 缺固定分区 '## {heading}'"
                "（分区固定、内容可空——空分区或「无」均合法；见 feat-plan-research 交付门禁）"
            )


def check_tasks(errors, warnings):
    for task_type in TASK_REQUIRED:
        root_dir = ROOT / task_type
        if not root_dir.exists():
            continue
        for entry in sorted(root_dir.iterdir()):
            if not entry.is_dir() or entry.name.startswith("."):
                continue
            if entry.name.lower() == "archive":
                # archive 任务也参与校验
                _check_archive(entry, task_type, errors, warnings)
                continue
            task_rel = f"{task_type}/{entry.name}"
            # CURRENT 用于判断状态（决定产物强制档位）
            cur = entry / "CURRENT.md"
            status = ""
            if cur.exists():
                status = (parse_current(cur) or {}).get("status", "")
            _check_products(entry, task_rel, task_type, status, errors)
            # CURRENT schema
            check_task_current(entry, task_rel, errors, warnings)


def _check_archive_entry(entry, task_rel, errors, warnings):
    """archive 内单任务：schema 校验 + 必须已完成（「必达已完成」跨类型不变量 + reopen 归档硬截止）。
    不跑 _check_products——历史任务旧产物档位/节名保留原貌（见 REVIEW_REQUIRED_HEADINGS 注释）；
    --staged 推导出 archive 任务目录时走本函数，与全量 _check_archive 同口径。"""
    check_task_current(entry, task_rel, errors, warnings)
    cur = entry / "CURRENT.md"
    if cur.exists():
        status = (parse_current(cur) or {}).get("status", "")
        if status != "已完成":
            errors.append(f"{task_rel}: archive 内状态 '{status}'（archive 必须 已完成；reopen 仅限活跃区）")


def _check_archive(archive_dir, task_type, errors, warnings):
    """archive 目录遍历入口（全量）；单任务校验见 _check_archive_entry。"""
    for entry in sorted(archive_dir.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        _check_archive_entry(entry, f"{task_type}/archive/{entry.name}", errors, warnings)


def check_index_alignment(errors, warnings, task_rel=None):
    """活跃任务目录必须在对应根目录 INDEX.md 登记（一行索引，WORKFLOW §2.3）。
    漏行 = 任务对「先查索引」的会话不可见。只查活跃区；archive 行对齐属后续治理，
    不在此扩。task_rel 限定单任务（--task 收尾门禁路径）。"""
    targets = []
    if task_rel:
        parts = task_rel.split("/")
        if len(parts) >= 3 and parts[1] == "archive":
            return  # archive 任务不查（历史行对齐另行治理）
        targets.append((parts[0], parts[-1]))
    else:
        for task_type in TASK_REQUIRED:
            root_dir = ROOT / task_type
            if not root_dir.exists():
                continue
            for entry in sorted(root_dir.iterdir()):
                if not entry.is_dir() or entry.name.startswith(".") or entry.name.lower() == "archive":
                    continue
                targets.append((task_type, entry.name))
    for task_type, name in targets:
        index = ROOT / task_type / "INDEX.md"
        if not index.exists():
            errors.append(f"{task_type}/INDEX.md 缺失（活跃任务须一行索引，WORKFLOW §2.3）")
            continue
        try:
            text = index.read_text(encoding="utf-8", errors="replace")
        except Exception:
            text = ""
        # 精确匹配表格行内 `<任务目录>/README.md`，避免任务名前缀或说明文字误命中。
        entry_re = re.compile(
            rf"(?<![A-Za-z0-9._-]){re.escape(name)}/README\.md(?=[#)\s|]|$)"
        )
        if not any(
            line.lstrip().startswith("|") and entry_re.search(line)
            for line in text.splitlines()
        ):
            errors.append(
                f"{task_type}/INDEX.md: 活跃任务 {name} 未登记（须一行索引，WORKFLOW §2.3）"
            )


# ─── 安全检查 ──────────────────────────────────────────────────────

# 疑似明文密钥（只报告文件:行号，不回显正文）
SUSPICIOUS_SECRET = re.compile(
    r"(glpat-[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{12,}|"
    r"xox[baprs]-[A-Za-z0-9-]{10,})"
)

# URL 内嵌凭证形态（https://user:pass@host）——专扫可提交的 .env（真实地址应放 .env.local）
ENV_URL_CRED_RE = re.compile(r"https?://[^\s/@:]+:[^\s/@]+@")


def _scan_py_danger(py, label, errors):
    """危险 Git / TLS / stash 模式扫描（label 用于报错定位：全量用文件名、--staged 用相对路径）。"""
    try:
        text = py.read_text(encoding="utf-8")
    except Exception:
        return
    # reset --hard：只匹配 git 调用列表形式（不匹配注释里空格分隔的 "reset --hard"）
    if '"reset", "--hard"' in text or "'reset', '--hard'" in text:
        errors.append(f"{label}: 含 reset --hard（破坏性 Git）")
    # CERT_NONE：只匹配实际赋值（不应出现）
    if "verify_mode = ssl.CERT_NONE" in text:
        errors.append(f"{label}: 含 CERT_NONE（TLS 证书校验关闭）")
    # check_hostname = False：实际赋值（workspace-check.py 已跳过，避免字符串误报）
    if "check_hostname = False" in text:
        errors.append(f"{label}: 关闭 hostname 校验")
    # 自动 stash push：git 调用列表形式（已移除）
    if '"stash", "push"' in text or "'stash', 'push'" in text:
        errors.append(f"{label}: 含自动 stash push（已移除）")


def _scan_secrets(p, label, errors):
    """明文密钥扫描（只报告 label:行号，不回显正文）。"""
    try:
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if SUSPICIOUS_SECRET.search(line):
                errors.append(f"安全: {label}:{i} 疑似明文密钥（不回显正文）")
    except Exception:
        pass


def check_security(errors, warnings):
    # 危险 Git / TLS 模式（.tools/*.py）
    # 跳过 workspace-check.py 自身（其检测模式字符串会自引用误报）
    for py in sorted(TOOLS.glob("*.py")):
        if py.name == "workspace-check.py":
            continue
        _scan_py_danger(py, py.name, errors)

    # 明文密钥扫描（仅 Git 跟踪的项目文档，排除 src/temp/.env.local；.env 可提交但不得含真实值）
    scan_targets = ["AGENTS.md", "README.md", "HUMAN.md", "WORKFLOW.md", "CHANGELOG.md",
                    ".tools/INDEX.md", ".env"]
    for rel in scan_targets:
        p = ROOT / rel
        if not p.exists():
            continue
        _scan_secrets(p, rel, errors)
        if rel == ".env":
            # URL 内嵌凭证形态（真实地址应放 .env.local）
            try:
                for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                    if ENV_URL_CRED_RE.search(line):
                        errors.append(f"安全: {rel}:{i} URL 内嵌凭证形态（真实地址应放 .env.local，不回显正文）")
            except Exception:
                pass


# ─── temp 卫生 ─────────────────────────────────────────────────────

def check_temp(errors, warnings):
    """temp/ 应只留 README.md 与操作者常驻 todo.md；其余残留告警（用完即清，见 WORKFLOW.md §7）。"""
    temp_dir = ROOT / "temp"
    if not temp_dir.exists():
        return
    allowed = {"README.md", "todo.md"}  # 常驻例外：README 说明 + todo.md 操作者待办
    for entry in sorted(temp_dir.iterdir()):
        if entry.name in allowed:
            continue
        rel = f"temp/{entry.name}"
        if entry.is_dir() and entry.name == "__pycache__":
            warnings.append(f"temp 卫生: {rel}/ 是 Python 运行缓存（该删，根 .gitignore 已排除 __pycache__）")
        elif entry.is_dir():
            warnings.append(f"temp 卫生: {rel}/ 残留（用完即清；有保留价值则移入对应任务目录，见 WORKFLOW.md §7）")
        else:
            warnings.append(f"temp 卫生: {rel} 残留（用完即清，见 WORKFLOW.md §7）")


# ─── worktree 卫生 ─────────────────────────────────────────────────

def _find_linked_worktrees(task_grp):
    """在 src/.worktrees/<task>/<namespace>/<repo> 深度找 linked worktree（.git 文件）。
    只深入到 repo 级，避开 node_modules 全量遍历。"""
    hits = []
    for ns in task_grp.iterdir():
        if not ns.is_dir():
            continue
        for repo in ns.iterdir():
            if not repo.is_dir():
                continue
            git_file = repo / ".git"
            if git_file.is_file():
                hits.append(repo)
    return hits


def _check_worktree_group(task_grp, warnings):
    """单个 src/.worktrees/<组> 的卫生检查（全量与 --task 共用）。"""
    rel = f"src/.worktrees/{task_grp.name}"
    active = _find_linked_worktrees(task_grp)
    if active:
        warnings.append(
            f"worktree 卫生: {rel}/ 仍有 {len(active)} 个活跃 linked worktree"
            f"（对应任务若已收尾，应授权移除 + 清理 *.code-workspace；见 WORKFLOW.md §7）"
        )
    else:
        warnings.append(
            f"worktree 卫生: {rel}/ 无活跃 worktree 的残留目录（收尾未清，应删）"
        )


def check_worktrees(errors, warnings):
    """src/.worktrees/ 孤儿检测：任务组目录有活跃 worktree（提醒收尾）或无 worktree 的残留壳（应删）。
    见 WORKFLOW.md §7。"""
    wt_root = ROOT / "src" / ".worktrees"
    if not wt_root.exists():
        return
    for task_grp in sorted(wt_root.iterdir()):
        if task_grp.is_dir():
            _check_worktree_group(task_grp, warnings)


def check_task_worktrees(task_path, warnings):
    """--task 用：只查该任务文档（任务目录 md）引用的 src/.worktrees/<组>——
    任务自产 worktree 的收尾自查，不带历史任务组噪音。"""
    wt_root = ROOT / "src" / ".worktrees"
    if not wt_root.exists():
        return
    groups = set()
    for md in task_path.glob("*.md"):
        text = md.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"src/\.worktrees/([A-Za-z0-9._-]+)", text):
            groups.add(m.group(1))
    for name in sorted(groups):
        grp = wt_root / name
        if grp.is_dir():
            _check_worktree_group(grp, warnings)


# ─── 登记完整性（入口真源须引用实际存在的实体；warning 档）──────────
#
# 防线：机制实例落地后入口真源失同步（2026-08-30 两实例：snapshots/ 落地
# 而 position/README 对比体系节未挂、快照「首次回顾时启用」状态句过时——
# 均靠操作者手动指出）。机器可判定优先于清单与自觉（坑条目三档判据）：
# 目录存在但入口真源零提及 = 孤儿 → warning，下次 check 自动浮出。

# 顶层目录豁免：工具/环境/隐藏目录（不属 README/AGENTS 目录表管辖）
_TOPDIR_EXEMPT = {".git", ".agents", ".tools", ".claude", ".codex", ".zcode",
                  ".github", ".vscode", "__pycache__", "node_modules", "archive"}


def check_registry_coverage(errors, warnings):
    """登记覆盖：① 顶层目录须在 README.md 或 AGENTS.md 出现；
    ② position/ 一级子目录须在 position/README.md 出现。孤儿 = warning。"""
    def _corpus(*names):
        buf = []
        for n in names:
            p = ROOT / n
            if p.exists():
                buf.append(p.read_text(encoding="utf-8", errors="replace"))
        return "\n".join(buf)

    top_corpus = _corpus("README.md", "AGENTS.md")
    for entry in sorted(ROOT.iterdir()):
        if not entry.is_dir() or entry.name in _TOPDIR_EXEMPT:
            continue
        if entry.name not in top_corpus:
            warnings.append(
                f"登记完整性: 顶层目录 {entry.name}/ 未在 README.md 或 AGENTS.md 目录表出现"
                f"（入口真源须随落地同步登记）"
            )
    pos_root = ROOT / "position"
    if pos_root.exists():
        pos_corpus = _corpus("position/README.md")
        for entry in sorted(pos_root.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name not in pos_corpus:
                warnings.append(
                    f"登记完整性: position/{entry.name}/ 未在 position/README.md 出现"
                    f"（对比体系节须随落地同步登记）"
                )


# ─── skill 真源单一性（.agents/skills 单一真源；防第三方工具副本漂移）──

# 禁止的 agent 专属 skills 副本目录（skills CLI 等会向检测到的 agent 目录写副本，单一真源之外全是漂移）
FORBIDDEN_SKILL_DIRS = [".zcode/skills", ".codex/skills"]

def check_skill_sources(errors, warnings):
    """skills 单一真源 = `.agents/skills/`：①禁 agent 专属副本目录（skills CLI 误写）；
    ②`.claude/skills` 存在时必须是指向 `.agents/skills` 的 junction/symlink（真目录副本会顶掉桥）。
    `.claude/skills` 缺失 = 换机/受让方未重建桥，属正常不报（重建见 .tools/skill-bridge/）。"""
    agents = ROOT / ".agents" / "skills"
    for rel in FORBIDDEN_SKILL_DIRS:
        if (ROOT / rel).exists():
            errors.append(
                f"skill 真源: {rel}/ 存在（agent 专属 skills 副本，单一真源应为 .agents/skills/；"
                f"skills CLI 误写，删除该目录——清理 SOP 见 VENDOR.md「管理命令」）"
            )
    bridge = ROOT / ".claude" / "skills"
    if bridge.exists() and os.path.realpath(bridge) != os.path.realpath(agents):
        errors.append(
            "skill 真源: .claude/skills 不是指向 .agents/skills 的 junction/symlink"
            "（真目录副本顶掉了桥；删副本后跑 .tools/skill-bridge/link-claude-skills.ps1 重建）"
        )


# ─── markdownlint（工具无关机器门禁）──────────────────────────────

MDLINT_LINE_RE = re.compile(
    r"^(.+?):(\d+)\s+(?:error|warning)\s+(MD\d+)/\S+\s+(.*)$"
)

# markdownlint 违规进 errors 还是 warnings（True=errors 阻塞；False=warnings 不阻塞）。
# 2026-08-29 转正 True（v1 同步批次落地；前置已满足：原范围存量违规清零）。
# 同日 B6 落地：`.agents/skills/**` 扩入 MDLINT_SCOPES——自有 skill 存量 121 处已清
#（agents-md-refiner / knowledge-base：--fix 格式修复 + 裸围栏语言标注 + 嵌套列表校正）。
MDLINT_AS_ERROR = True

# markdownlint-cli2 版本——跟随 VSCode 扩展内嵌版本（避免 npx 拉最新导致规则集漂移）。
# 升级 VSCode 扩展后，查其 package.json 的 "markdownlint-cli2" 依赖版本，同步本常量：
#   grep markdownlint-cli2 <扩展目录>/package.json
# 当前：VSCode 扩展 v0.62.1 内嵌 cli2 0.23.2（markdownlint v0.41.1，53 条活跃规则）
MDLINT_CLI2_VERSION = "0.23.2"

# 依赖链 markdownlint-cli2@0.23.2 → markdownlint@0.41 → string-width@8 在模块顶层用 /v 正则
# （string-width/index.js:19 起）。Node <20 不支持 v flag，模块加载即 SyntaxError（2026-08-13 实发：
# 症状=「非零退出 code=1 但未解析到违规；首行：.../string-width/index.js:19」）。npx 走 PATH 解析，
# 本机 scoop-nvm 多 Node 版本共存，某会话 PATH 挂旧版 Node 即触发 → 检查前先验 node 主版本。
MDLINT_MIN_NODE_MAJOR = 20

# 显式 lint 范围（经验证 .markdownlintignore 无消费者：markdownlint-cli2 v0.23 不读、
# VSCode 扩展 v0.62.1 实时 lint 也不读 → 已删除该文件）。workspace-check 是唯一忽略控制点。
# 排除：src/（独立 repo）、.agents/commands（薄路由随 skill 正文维护）、temp/、
# retrospectives/、workspace-grills/（历史冻结）、各 dot 配置目录。
# .agents/skills：自有 skill 检（B6，2026-08-29 扩入）；vendor skill 豁免见 _vendor_skill_dirs。
MDLINT_SCOPES = [
    "*.md",
    ".agents/skills/**/*.md",
    "notes/**/*.md",
    "exps/**/*.md",
    "workspace-optimize/**/*.md",
    "case/**/*.md",
    "story/**/*.md",
    "tech/**/*.md",
    "research/**/*.md",
    "reference/**/*.md",
]

# 任务 archive 排除（历史冻结先例同 retrospectives/workspace-grills）：归档文件按当年规则
# 写成、reopen 硬截止不再变更——新规则收紧不应让历史文件拦现行全量门禁（MDLINT_AS_ERROR
# 下即阻塞），也不再付扫描成本；追溯走冷层定向读（WORKFLOW §2.2）。
MDLINT_ARCHIVE_NEGATIONS = [f"!{t}/archive/**" for t in TASK_REQUIRED]


# 手动 vendor 目录（不入 lock 的 vendor：local 源复制 / 官方 zip 手动 vendor；
# 真源 = .agents/skills/INDEX.md「vendor 的第三方 skill」表，新增手动 vendor 时同步这里。
# 本仓当前 vendor 全部经 skills-lock.json 管理，故为空集）
MANUAL_VENDOR_SKILL_DIRS = set()


def _vendor_skill_dirs():
    """vendor skill 目录集合 = lock 内 remote（单一真源 skills-lock.json）+ 手动 vendor（上方静态清单）。
    vendor skill 随源、不改骨架（INDEX 开篇约定），SKILL.md 不按本仓规则检，
    全量与 --staged 口径一致豁免（plainness 同用）。"""
    try:
        lock = json.loads((ROOT / "skills-lock.json").read_text(encoding="utf-8"))
        dirs = {f".agents/skills/{name}" for name in lock.get("skills", {})}
    except Exception:
        dirs = set()  # lock 缺失/损坏不阻断检查，仅失去该部分豁免（lock 内 vendor 会被照扫）
    return dirs | MANUAL_VENDOR_SKILL_DIRS


# MDLINT_SCOPES 的文件级等价判定（--staged 用）：与 glob 口径一致——"<dir>/**/*.md"
# 等价于前缀 "<dir>/"。不用首段目录名集合：多级 scope（.agents/skills）下会放宽到
# 整个 .agents（commands 等非 lint 范围文件误入）。
# 形态约束：含 / 的 scope 必形如 "<dir>/**/*.md"（前缀推导依赖 /** 切分）。
_bad_scopes = [p for p in MDLINT_SCOPES if "/" in p and "/**/" not in p]
if _bad_scopes:
    raise ValueError(f"MDLINT_SCOPES 含不支持的形态（须 <dir>/**/*.md）: {_bad_scopes}")
MDLINT_SCOPE_PREFIXES = tuple(
    p[: p.index("/**")] + "/" for p in MDLINT_SCOPES if "/" in p
)


def _in_mdlint_scope(rel):
    """暂存文件是否属 markdownlint 显式范围（与全量 MDLINT_SCOPES 口径一致，防 staged 查全量不查的文件）。"""
    if not rel.endswith(".md"):
        return False
    parts = rel.split("/")
    # 任务 archive 历史冻结排除（与全量否定 glob 口径一致，见 MDLINT_ARCHIVE_NEGATIONS）
    if len(parts) >= 2 and parts[1] == "archive" and parts[0] in TASK_REQUIRED:
        return False
    # vendor skill 豁免（与全量 !{dir}/** 负 glob 口径一致，随源不检）
    if any(rel.startswith(f"{v}/") for v in _vendor_skill_dirs()):
        return False
    return "/" not in rel or rel.startswith(MDLINT_SCOPE_PREFIXES)


def check_markdownlint(errors, warnings, scope=None, files=None):
    """跑 markdownlint-cli2（npx 免全局装，工具无关）。
    scope=Path 时只扫该目录下 **/*.md；files=[相对路径] 时只查这些文件（--staged 用）；
    都为 None 时扫全量（按 MDLINT_SCOPES，见下方）。
    违规进 errors（MDLINT_AS_ERROR=True）；降级 warnings 改 False。
    规则真源是 .markdownlint.jsonc（ROOT）。"""
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        warnings.append("markdownlint: 未找到 npx（跳过；装 Node.js 后可用）")
        return
    # Node 版本守卫：旧 Node（<20）加载 string-width@8 即崩（见 MDLINT_MIN_NODE_MAJOR 注释）。
    node = shutil.which("node")
    if node:
        try:
            rv = subprocess.run(
                [node, "--version"], capture_output=True, text=True, timeout=15,
            )
            ver = (rv.stdout or "").strip()
            m = re.match(r"v(\d+)\.", ver)
            if rv.returncode == 0 and m and int(m.group(1)) < MDLINT_MIN_NODE_MAJOR:
                warnings.append(
                    f"markdownlint: node {ver} < v{MDLINT_MIN_NODE_MAJOR}"
                    f"（string-width@8 用 /v 正则，旧 Node 加载即崩，非文档问题）——"
                    f"切 Node ≥ {MDLINT_MIN_NODE_MAJOR} 后重跑"
                )
                return
        except Exception:
            pass  # 版本探测失败不阻断 lint 本身（保持原有行为）
    if files is not None:
        # cli2 位置参数按 glob 解释：路径含 [ ? * 时静默匹配 0 文件且 exit=0；
        # 前缀 : 声明字面路径（cli2 官方语法），防门禁静默放行
        globs = [f":{rel}" for rel in files]
    elif scope is not None:
        try:
            rel = scope.relative_to(ROOT).as_posix()
        except ValueError:
            rel = str(scope).replace("\\", "/")
        globs = [f"{rel}/**/*.md"]
    else:
        # workspace-check 唯一忽略控制点（cli2/VSCode 扩展都不读 .markdownlintignore，已删）。
        # vendor skill 目录追加否定 glob（cli2 支持 ! 前缀），随源不检；任务 archive 同（历史冻结）
        globs = list(MDLINT_SCOPES) + [f"!{v}/**" for v in sorted(_vendor_skill_dirs())] + MDLINT_ARCHIVE_NEGATIONS

    cmd = [npx, "--yes", f"markdownlint-cli2@{MDLINT_CLI2_VERSION}"] + globs
    try:
        proc = subprocess.run(
            cmd, cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=180,
        )
    except subprocess.TimeoutExpired:
        warnings.append("markdownlint: 执行超时（>180s，可能 npx 首次下载 markdownlint-cli2）")
        return
    except Exception as e:
        warnings.append(f"markdownlint: 调用失败 {e}")
        return

    out = (proc.stdout or "") + (proc.stderr or "")
    found = []
    for line in out.splitlines():
        m = MDLINT_LINE_RE.match(line.strip())
        if m:
            found.append((m.group(1), m.group(2), m.group(3), m.group(4)))

    if not found and proc.returncode != 0:
        first = out.splitlines()[0] if out else "(空)"
        warnings.append(f"markdownlint: 非零退出 code={proc.returncode} 但未解析到违规；首行：{first}")
        return

    bucket = errors if MDLINT_AS_ERROR else warnings
    tag = "markdownlint" + ("" if MDLINT_AS_ERROR else "（warning，未阻塞）")
    for f, ln, rule, msg in found:
        bucket.append(f"{tag}: {f}:{ln} {rule} {msg}")


# ─── 登记对源侧一致性（B2③；实现外置 _registration_check.py）──────────
#
# 分区实现必然引用构建脚本文件名，内联会构成开源产物残留词——独立成模块，
# 构建时随元工序配套移除；缺席即 no-op（开源产物态无构建管线，分区自动下线）。

try:
    from _registration_check import check_registration_pairs
except ImportError:
    if (TOOLS / "_registration_check.py").exists():
        raise  # 模块在而导入失败 = 工具自身 bug，不静默降级（防线无声消失）
    def check_registration_pairs(errors, warnings, files=None):
        """开源产物态：无构建管线，登记对分区缺席（no-op）。"""
        return


# ─── 平实度（机制文档「说人话」，warning 档）────────────────────────
#
# 机制文档「生产者逻辑 ≠ 消费者逻辑」——单行/单段密度过大致常规阅读失效。四指标
# 阈值起步宽松（warning 档防告警爆炸）：
#   ① 单行字符：正文/列表/标题行 >400
#   ② 表格行（| 开头）>600（多列形态天然更长）
#   ③ 散文段长度：连续纯文本行（排除围栏/表格/列表/标题/引用）合计 >400
#   ④ 例外条款括号嵌套（（）与 () 合计）≥3 层（「例外之例外之例外」形态）
# 范围：WORKFLOW/AGENTS/BACKLOG + 根一层目录 INDEX.md（含 .tools）+ .agents/skills/INDEX.md
# + 自有 skill SKILL.md（vendor 豁免复用 _vendor_skill_dirs，本体不改不检）+ 活跃任务产物
# （五任务根非 archive 目录内 *.md；归档不占上下文不扫，run-*/evals-run* 冻结快照不回改、
# 同不检）。frontmatter（首对 --- 之间）与围栏代码块跳过：description 是 YAML 单串不可拆、
# 代码行非散文。触发信号（连续两期新增/修改段落超阈值）→ 升 error 档。

PLAINNESS_LINE_LIMIT = 400        # 正文/列表/标题行字符上限
PLAINNESS_TABLE_LINE_LIMIT = 600  # 表格行字符上限
PLAINNESS_PARA_LIMIT = 400        # 散文段（连续纯文本行）合计字符上限
PLAINNESS_NEST_DEPTH = 3          # 括号嵌套层数上限（≥3 报）


def _is_frozen_snapshot(name):
    """冻结快照（run-*/evals-run* 执行快照落盘后不回改纪律）——plainness 不检。"""
    return name.startswith("run-") or name.startswith("evals-run")


def _plainness_targets():
    """平实度检查文件集（范围声明见上方分区注释；活跃任务产物含 / 归档与冻结快照排除口径同注释）。"""
    rels = ["WORKFLOW.md", "AGENTS.md", "BACKLOG.md"]
    for d in sorted(ROOT.iterdir()):
        if d.is_dir() and (d / "INDEX.md").is_file():
            rels.append(f"{d.name}/INDEX.md")
    if (ROOT / ".agents/skills/INDEX.md").is_file():
        rels.append(".agents/skills/INDEX.md")
    vendors = _vendor_skill_dirs()
    for p in sorted(ROOT.glob(".agents/skills/*/SKILL.md")):
        if f".agents/skills/{p.parent.name}" not in vendors:
            rels.append(f".agents/skills/{p.parent.name}/SKILL.md")
    for task_type in TASK_REQUIRED:
        root = ROOT / task_type
        if not root.is_dir():
            continue
        for entry in sorted(root.iterdir()):
            if not entry.is_dir() or entry.name.startswith(".") or entry.name.lower() == "archive":
                continue
            rels += [
                f"{task_type}/{entry.name}/{p.name}"
                for p in sorted(entry.glob("*.md"))
                if not _is_frozen_snapshot(p.name)
            ]
    return [r for r in rels if (ROOT / r).is_file()]


def _nest_depth(line):
    """括号嵌套最大深度（中英文括号合计；闭括号多余只钳到 0，不产生负深度误判）。"""
    depth = mx = 0
    for ch in line:
        if ch in "(（":
            depth += 1
            mx = max(mx, depth)
        elif ch in ")）":
            depth = max(0, depth - 1)
    return mx


_PLAIN_STRUCTURAL = ("#", "|", ">", "-", "*", "+")


def _para_is_structural(s):
    return s.startswith(_PLAIN_STRUCTURAL) or (
        len(s) > 2 and s[0].isdigit() and s[1] in ".）)"
    )


def check_doc_plainness(warnings, files=None):
    """机制文档平实度四指标（warning 档不阻塞；指标/阈值/范围见分区注释）。
    files=[相对路径] 时只查这些文件（--staged/--task 用）；None 查全量目标集。
    输出按文件×指标聚合（每文件每指标一条 + 首例行号），防 INDEX 层残余超限刷屏。"""
    for rel in files if files is not None else _plainness_targets():
        p = ROOT / rel
        if not p.is_file():
            continue
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        if lines and lines[0].strip() == "---":  # 去 frontmatter（description 单串不可拆）
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    lines = lines[i + 1:]
                    break
        over_lines, paras, over_nest = [], [], []
        in_fence = False
        cur_len, cur_start = 0, 0

        def _flush():
            nonlocal cur_len
            if cur_len:
                paras.append((cur_start, cur_len))
                cur_len = 0

        for i, l in enumerate(lines, 1):
            s = l.strip()
            if s.startswith("```"):
                in_fence = not in_fence
                _flush()
                continue
            if in_fence or not s:
                _flush()
                continue
            limit = PLAINNESS_TABLE_LINE_LIMIT if s.startswith("|") else PLAINNESS_LINE_LIMIT
            if len(l) > limit:
                over_lines.append((i, len(l)))
            d = _nest_depth(l)
            if d >= PLAINNESS_NEST_DEPTH:
                over_nest.append((i, d))
            if _para_is_structural(s):
                _flush()
                continue
            if cur_len == 0:
                cur_start = i
            cur_len += len(l)
        _flush()
        over_paras = [(st, n) for st, n in paras if n > PLAINNESS_PARA_LIMIT]
        if over_lines:
            worst = max(over_lines, key=lambda t: t[1])
            warnings.append(
                f"平实度: {rel} {len(over_lines)} 行超限"
                f"（正文>{PLAINNESS_LINE_LIMIT}/表格>{PLAINNESS_TABLE_LINE_LIMIT}；"
                f"最长 {worst[1]}，首例 :{over_lines[0][0]}）"
            )
        if over_paras:
            warnings.append(
                f"平实度: {rel} {len(over_paras)} 个散文段超 {PLAINNESS_PARA_LIMIT} 字符"
                f"（首例 :{over_paras[0][0]}）"
            )
        if over_nest:
            warnings.append(
                f"平实度: {rel} {len(over_nest)} 行括号嵌套 ≥{PLAINNESS_NEST_DEPTH} 层"
                f"（首例 :{over_nest[0][0]}）"
            )


# ─── --staged 暂存集聚焦（lint-staged 式，commit 前机器门禁）────────

def _git_staged_files():
    """git diff --cached 暂存文件清单（-z 防路径特殊字符切割）；失败返回 None。
    utf-8 errors="replace"：非 UTF-8 路径会产生替换字符 → 下游 is_file() 为 False 被跳过
    （本仓路径全 UTF-8，接受的理论边角）。"""
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "diff", "--cached", "--name-only", "-z"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        )
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    return [p for p in proc.stdout.split("\0") if p]


def _task_dirs_from(rel_paths):
    """从暂存路径推导涉及的任务目录（story/xxx、story/archive/xxx、workspace-optimize/xxx…）。"""
    dirs = set()
    for rel in rel_paths:
        parts = rel.split("/")
        if parts[0] not in TASK_REQUIRED or len(parts) < 2:
            continue
        if len(parts) >= 3 and parts[1] == "archive":
            dirs.add("/".join(parts[:3]))
        else:
            dirs.add("/".join(parts[:2]))
    return sorted(dirs)


def check_staged_security(rel_paths, errors):
    """--staged 密钥/危险模式扫描：暂存 .tools/*.py 走危险模式（跳过本工具自引用），
    其余暂存文本文件（.md/.json/.jsonc/.txt/.sh/.ps1）走明文密钥扫描。"""
    for rel in rel_paths:
        p = ROOT / rel
        if not p.is_file():
            continue
        if rel.startswith(".tools/") and rel.endswith(".py"):
            if p.name != "workspace-check.py":
                _scan_py_danger(p, rel, errors)
        elif rel.endswith((".md", ".json", ".jsonc", ".txt", ".sh", ".ps1")):
            _scan_secrets(p, rel, errors)


def check_staged_tasks(rel_paths, errors, warnings):
    """--staged 任务检查：schema/产物 + 活跃任务 INDEX 对齐；archive 保持历史豁免口径。"""
    for td in _task_dirs_from(rel_paths):
        tp = ROOT / td
        if not tp.is_dir():
            continue
        parts = td.split("/")
        if len(parts) >= 3 and parts[1] == "archive":
            _check_archive_entry(tp, td, errors, warnings)
            continue
        check_task_current(tp, td, errors, warnings)
        cur = tp / "CURRENT.md"
        status = (parse_current(cur) or {}).get("status", "") if cur.exists() else ""
        _check_products(tp, td, parts[0], status, errors)
        check_index_alignment(errors, warnings, task_rel=td)


# ─── main ──────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="工作区一致性只读检查")
    ap.add_argument("--section", choices=["all", "tasks", "security", "versions", "temp", "worktrees", "skills", "markdownlint", "registration", "plainness", "coverage", "links", "protocols"],
                    default="all", help="只检查某个分区")
    ap.add_argument("--task", metavar="REL", default=None,
                    help="限定到单个任务目录（如 workspace-optimize/task-2026-08-11-xxx）；只跑 tasks(schema+产物) + markdownlint，跳过全局检查")
    ap.add_argument("--staged", action="store_true",
                    help="lint-staged 式暂存集聚焦：只检查 git diff --cached 的文件"
                         "（markdownlint / 任务 schema+产物与 INDEX 对齐 / 链接 / 密钥扫描 /"
                         "平实度 / 登记对按文件聚焦，WORKFLOW/CHANGELOG 在集时附带版本一致性）；"
                         "跳过全局分区（worktrees/temp/skills/coverage/protocols 与 links 全量"
                         "——收尾按 --task/全量覆盖）")
    args = ap.parse_args()

    if args.staged and (args.task or args.section != "all"):
        ap.error("--staged 与 --task/--section 互斥")

    errors, warnings = [], []

    staged = None
    if args.staged:
        staged = _git_staged_files()
        if staged is None:
            errors.append("--staged: 读取暂存区失败（git diff --cached）")
        elif not staged:
            warnings.append("--staged: 暂存区为空，无可检查文件")
        else:
            existing = [rel for rel in staged if (ROOT / rel).is_file()]
            # markdownlint：限显式 lint 范围内的暂存 .md（口径与全量 MDLINT_SCOPES 一致）
            md_files = [rel for rel in existing if _in_mdlint_scope(rel)]
            if md_files:
                check_markdownlint(errors, warnings, files=md_files)
            # 任务 schema / 产物门禁 / INDEX 对齐（archive 保持历史豁免口径）
            check_staged_tasks(staged, errors, warnings)
            # links / 密钥与危险模式（按文件聚焦）
            check_staged_links(existing, warnings)
            check_staged_security(staged, errors)
            # 平实度：暂集内机制文档按文件查（口径与全量 plainness 分区一致，warning 档）
            pl_files = [rel for rel in existing if rel in set(_plainness_targets())]
            if pl_files:
                check_doc_plainness(warnings, files=pl_files)
            # 登记对：暂存集含登记面文件时核验（旧串漂移当场报，不等构建期 MISS）
            check_registration_pairs(errors, warnings, files=set(existing))
            # 版本一致性：WORKFLOW/CHANGELOG 在暂存集时附带（两者便宜且常成对改动）
            if "WORKFLOW.md" in staged or "CHANGELOG.md" in staged:
                check_versions(errors)
    elif args.task:
        # 单目录增量模式：任务收尾聚焦用，只验当前任务
        task_path = ROOT / args.task
        if not task_path.is_dir():
            errors.append(f"--task 路径不存在或非目录：{args.task}")
        else:
            task_type = args.task.split("/")[0] if "/" in args.task else ""
            if task_type in TASK_REQUIRED:
                check_task_current(task_path, args.task, errors, warnings)
                cur = task_path / "CURRENT.md"
                status = (parse_current(cur) or {}).get("status", "") if cur.exists() else ""
                _check_products(task_path, args.task, task_type, status, errors)
                check_index_alignment(errors, warnings, task_rel=args.task)
            else:
                warnings.append(f"--task '{args.task}' 非已知任务类型（{list(TASK_REQUIRED)}），跳过 schema/产物检查")
            # 归档任务历史冻结豁免（与全量 MDLINT_ARCHIVE_NEGATIONS 口径一致）：
            # archive 不受现行 lint/平实度门禁约束，--task 模式仅查 schema 与产物
            _parts = args.task.split("/")
            if len(_parts) >= 2 and _parts[1] == "archive":
                warnings.append(
                    f"--task '{args.task}' 为归档任务：markdownlint/平实度冻结豁免（与全量口径一致）"
                )
            else:
                check_markdownlint(errors, warnings, scope=task_path)
                # 平实度：任务产物随收尾门禁顺带查（warning 档；范围 = 任务目录内 *.md，冻结快照同豁免）
                check_doc_plainness(
                    warnings,
                    files=[
                        p.relative_to(ROOT).as_posix()
                        for p in sorted(task_path.glob("*.md"))
                        if not _is_frozen_snapshot(p.name)
                    ],
                )
            # worktree 自查：只查该任务 md 引用的 src/.worktrees/<组>（不带历史任务组噪音）
            check_task_worktrees(task_path, warnings)
            # temp 自查（B2①，2026-08-29 接入）：收尾聚焦模式同查全局 temp 残留
            #（任务自产 temp 是常态残留源，收尾即拦；与 worktrees 批次二对称补齐）
            check_temp(errors, warnings)
    else:
        if args.section in ("all", "versions"):
            check_versions(errors)
        if args.section in ("all", "tasks"):
            check_tasks(errors, warnings)
            check_index_alignment(errors, warnings)
        if args.section in ("all", "security"):
            check_security(errors, warnings)
        if args.section in ("all", "temp"):
            check_temp(errors, warnings)
        if args.section in ("all", "worktrees"):
            check_worktrees(errors, warnings)
        if args.section in ("all", "skills"):
            check_skill_sources(errors, warnings)
        if args.section in ("all", "markdownlint"):
            check_markdownlint(errors, warnings)
        if args.section in ("all", "registration"):
            check_registration_pairs(errors, warnings)
        if args.section in ("all", "plainness"):
            check_doc_plainness(warnings)
        if args.section in ("all", "coverage"):
            check_registry_coverage(errors, warnings)
        if args.section in ("all", "links"):
            check_md_links(errors, warnings)
        if args.section in ("all", "protocols"):
            check_protocols(errors, warnings)

    # 输出
    scope_label = "staged" if args.staged else (f"task={args.task}" if args.task else f"section={args.section}")
    print("=" * 60)
    print(f"  workspace-check（{scope_label}）")
    print("=" * 60)
    if errors:
        print(f"\n[ERROR] {len(errors)} 项必须修复：")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print(f"\n[WARN] {len(warnings)} 项启发式告警：")
        for w in warnings:
            print(f"  ⚠ {w}")
    if not errors and not warnings:
        print("\n[OK] 全部通过")

    print(f"\n# 结果: errors={len(errors)} warnings={len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main() or 0)
