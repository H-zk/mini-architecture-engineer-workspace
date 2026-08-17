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
    per-status next/blocker 与产物档位按类型声明；workspace-optimize 已完成需 review 事件 passed/legacy-exempt）
  - 正式产物存在（按任务类型 + 状态档位；archive 内必须已完成；
    story review.md 到强制档位须含固定分区「## 无法决策点」——内容可空，查分区存在性）
  - Markdown 链接/章节引用有效性（links 分区：本地链接存在性 + WORKFLOW §N.M 引用，warning 级）
  - 协议骨架复写（protocols 分区：通用协议句仅许在 WORKFLOW，skill 内命中或指纹真源失配 → warning）
  - 安全检查（reset --hard / CERT_NONE / 关闭 hostname / 疑似明文密钥）
  - temp 卫生（temp/ 应只留 README.md，其余残留告警）
  - worktree 卫生（src/.worktrees/ 孤儿/残留告警）
  - markdownlint（调 markdownlint-cli2，规则真源 .markdownlint.jsonc）

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
  python .tools/workspace-check.py --section links
  python .tools/workspace-check.py --section protocols
  python .tools/workspace-check.py --task workspace-optimize/task-YYYY-MM-DD-xxx   # 单目录增量（任务收尾聚焦）
  python .tools/workspace-check.py --staged   # 暂存集聚焦（lint-staged 式，commit 前机器门禁：
                                               # 只检查 git diff --cached 的文件，与收尾门禁互补）
"""
import argparse
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
    """--staged：链接/§引用检查聚焦暂存文件（限全量覆盖面：根层常驻文档 + skills + exps）。"""
    valid_secs = _wf_valid_secs()
    if valid_secs is None:
        return
    for rel in rel_paths:
        p = ROOT / rel
        in_universe = rel in _LINK_UNIVERSE_ROOT or (
            (rel.startswith(".agents/skills/") or rel.startswith("exps/")) and rel.endswith(".md")
        )
        if not in_universe or not p.is_file():
            continue
        _check_links_existence(p, warnings)
        if rel in _SEC_REF_ROOT or rel.startswith(".agents/skills/"):
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


def check_worktrees(errors, warnings):
    """src/.worktrees/ 孤儿检测：任务组目录有活跃 worktree（提醒收尾）或无 worktree 的残留壳（应删）。
    见 WORKFLOW.md §7。"""
    wt_root = ROOT / "src" / ".worktrees"
    if not wt_root.exists():
        return
    for task_grp in sorted(wt_root.iterdir()):
        if not task_grp.is_dir():
            continue
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
# 首版 False（观察一迭代后可转 True）。
MDLINT_AS_ERROR = False

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
# 排除：src/（独立 repo）、.agents/（skill 目录，后续迭代单独覆盖）、temp/、
# retrospectives/、workspace-grills/（历史冻结）、各 dot 配置目录。
MDLINT_SCOPES = [
    "*.md",
    "notes/**/*.md",
    "exps/**/*.md",
    "workspace-optimize/**/*.md",
    "case/**/*.md",
    "story/**/*.md",
    "tech/**/*.md",
    "research/**/*.md",
    "reference/**/*.md",
]


# MDLINT_SCOPES 的文件级等价判定（--staged 用）：根层 .md 或首段目录在下列集合内
MDLINT_SCOPE_DIRS = {p.split("/")[0] for p in MDLINT_SCOPES if "/" in p}


def _in_mdlint_scope(rel):
    """暂存文件是否属 markdownlint 显式范围（与全量 MDLINT_SCOPES 口径一致，防 staged 查全量不查的文件）。"""
    if not rel.endswith(".md"):
        return False
    return "/" not in rel or rel.split("/")[0] in MDLINT_SCOPE_DIRS


def check_markdownlint(errors, warnings, scope=None, files=None):
    """跑 markdownlint-cli2（npx 免全局装，工具无关）。
    scope=Path 时只扫该目录下 **/*.md；files=[相对路径] 时只查这些文件（--staged 用）；
    都为 None 时扫全量（按 MDLINT_SCOPES，见下方）。
    违规默认进 warnings（MDLINT_AS_ERROR=False）；转 error 改 MDLINT_AS_ERROR=True。
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
        globs = MDLINT_SCOPES

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


# ─── main ──────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="工作区一致性只读检查")
    ap.add_argument("--section", choices=["all", "tasks", "security", "versions", "temp", "worktrees", "skills", "markdownlint", "links", "protocols"],
                    default="all", help="只检查某个分区")
    ap.add_argument("--task", metavar="REL", default=None,
                    help="限定到单个任务目录（如 workspace-optimize/task-2026-08-11-xxx）；只跑 tasks(schema+产物) + markdownlint，跳过全局检查")
    ap.add_argument("--staged", action="store_true",
                    help="lint-staged 式暂存集聚焦：只检查 git diff --cached 的文件"
                         "（markdownlint / 任务 schema+产物 / links / 密钥扫描按文件跑，"
                         "WORKFLOW/CHANGELOG 在集时附带版本一致性）；"
                         "跳过全局分区（worktrees/temp/protocols，收尾按 --task/全量覆盖）")
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
            # 任务 schema / 产物门禁：从暂存路径推导任务目录（整目录删除无对象可查，跳过）；
            # archive 任务走 _check_archive_entry 同口径（只查 schema + 必须已完成，不跑产物门禁）
            for td in _task_dirs_from(staged):
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
            # links / 密钥与危险模式（按文件聚焦）
            check_staged_links(existing, warnings)
            check_staged_security(staged, errors)
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
            else:
                warnings.append(f"--task '{args.task}' 非已知任务类型（{list(TASK_REQUIRED)}），跳过 schema/产物检查")
            check_markdownlint(errors, warnings, scope=task_path)
    else:
        if args.section in ("all", "versions"):
            check_versions(errors)
        if args.section in ("all", "tasks"):
            check_tasks(errors, warnings)
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
