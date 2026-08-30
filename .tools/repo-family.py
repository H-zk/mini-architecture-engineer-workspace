#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""repo-family.py — 仓库家族判定（只读，信号现算）

家族是**派生视图**不是静态属性：按信号现算各仓「基准分支 + 版本职责」，不存清单
（与 WORKFLOW §2.6「现状靠算不存」同哲学）。重跑两次 diff 输出 = 家族漂移检测
（如某仓基准分支从 develop-N 迁移到 develop、版本规则迁移到新后缀）。

信号（按优先级）：
  1. 语言栈：根 pom.xml → 后端（pom SNAPSHOT/RELEASE 体系）；
     根或一级子目录 package.json → 前端
  2. 分支形态：develop-N / develop / develop-<别名> / release-YYYYMMDD /
     master-main 候选线
  3. 分支新近度：候选线取 committerdate 最新者为活跃线（破「双线」歧义；
     第二活跃 develop-N 距最新 <30 天 → 多产品线并行旗标）
  4. 版本格式（monorepo 感知：根 version 静态时读 packages/*/、packages/*/*/，
     按 dev-sprint > dev.N > 非静态 优先取）

【模板占位 · 信号配置区】下方「信号正则与配置」块须按你实际仓群的分支/版本体系
重配后再用（默认给通用 gitflow 形态；develop-N 默认线、特定版本后缀等约定因仓群
而异，见 AGENTS「代码视图隔离 · 基准分支判定」）。重配点：
  - DEFAULT_DN_LINE：你仓群文档化的默认开发线（平局优先），无则留 None
  - DEV_*_RE：版本串后缀正则（按你的版本体系，如 -rc.1 / -beta.2 / -dev.20260829.1）
  - OVERRIDES / ALIASES / EXCLUDE_NS：空表起步，仅收信号不可见的混合态

覆盖表（OVERRIDES，仅收信号不可见的混合态，勿当仓库存放处膨胀）：
  宿主型 / 多产品线 / 判定器失效兜底；新条目须先证明信号判不了。

用法：
  python .tools/repo-family.py                    # 全部仓库（表格）
  python .tools/repo-family.py --repo <name>      # 名称子串过滤
  python .tools/repo-family.py --json             # 机器可读（feat 任务消费）
  python .tools/repo-family.py --src <dir>        # 仓库根目录（默认工作区 src/，测试用）

安全：只读（git for-each-ref / show / rev-parse），不联网、不碰凭证、不写文件。
低置信 / 有旗标 → 开工时咨询操作者，不假设（AGENTS「代码视图隔离」）。
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SRC_DEFAULT = Path(__file__).resolve().parent.parent / "src"
EXCLUDE_NS = set()  # 【模板占位】非业务仓库根（namespace），按需登记

# ── 信号正则与配置（【模板占位】按仓群重配，见模块 docstring）──────────
# 迭代日期版后缀（示例形态：-dev-20260829.1 / -rc-20260829.1）
DEV_SPRINT_RE = re.compile(r"-(?:dev|rc)-\d{8}\.\d+$")
# 递增号版后缀（示例形态：-dev.3 / -beta.2 / -rc.1）
DEV_NUM_RE = re.compile(r"-(?:dev|develop|beta)\.\d+(?:-rc\.\d+)?$")
# 迭代发布分支（release-YYYYMMDD）
SPRINT_REL_RE = re.compile(r"^release-(\d{8})$")
# 数字后缀开发线（develop-1 / develop-2 …）
DN_RE = re.compile(r"^develop-\d+$")
# 文档化默认开发线（平局时优先；无约定留 None）
DEFAULT_DN_LINE = None
STATIC_VERSIONS = {"1.0.0", "0.0.0", "0.0.1", "1.0.1"}

# 混合态覆盖表：repo 名 → 覆盖/备注（仅信号不可见时才加；空表起步）
OVERRIDES = {}

# 高频口语别名 → 仓库名（--repo 过滤用，保持极小；空表起步）
ALIASES = {}


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else ""


def _remote_prefix(repo: Path) -> str:
    """有 origin 远端引用用 origin/，否则（隔离测试）用本地分支。"""
    return "origin/" if _git(repo, "for-each-ref", "refs/remotes/origin/") else ""


def _branch_dates(repo: Path) -> dict:
    """分支名 → committerdate（YYYY-MM-DD）。"""
    prefix = _remote_prefix(repo)
    ref = "refs/remotes/origin/" if prefix else "refs/heads/"
    out = _git(repo, "for-each-ref", "--sort=-committerdate",
               "--format=%(refname:short) %(committerdate:short)", ref)
    dates = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        short = parts[0]
        # origin/HEAD 经 refname:short 可能缩写为 "origin"（无斜杠），一并过滤
        if short in ("origin", "HEAD") or short.endswith("/HEAD"):
            continue
        if prefix:
            if "/" not in short:
                continue
            dates[short.split("/", 1)[1]] = parts[1]
        else:
            dates[short] = parts[1]
    return dates


def _pick_version(versions: list) -> str:
    """monorepo 多包版本取最有信息量的：迭代日期版 > 递增号版 > 非静态。"""
    for pat in (DEV_SPRINT_RE, DEV_NUM_RE):
        for v in versions:
            if pat.search(v):
                return v
    for v in versions:
        if v and v not in STATIC_VERSIONS:
            return v
    return versions[0] if versions else ""


def _read_version(repo: Path, branch: str, sub_pkg_dirs: list) -> tuple:
    """读 branch 上版本串 → (版本串, 是否 monorepo/子目录兜底)。"""
    prefix = _remote_prefix(repo)
    ref = f"{prefix}{branch}"
    if (repo / "pom.xml").exists():
        out = _git(repo, "show", f"{ref}:pom.xml") or ""
        out = re.sub(r"<parent>.*?</parent>", "", out, flags=re.S)  # 跳过 parent 块
        for m in re.finditer(r"<version>([^<]+)</version>", out):
            if "${" not in m.group(1):
                return m.group(1), False
        return "", False

    paths = ["package.json"] + [f"{d}/package.json" for d in sub_pkg_dirs]
    root_out = _git(repo, "show", f"{ref}:package.json")
    m = re.search(r'"version"\s*:\s*"([^"]+)"', root_out or "")
    root_ver = m.group(1) if m else ""
    versions = [root_ver] if root_ver else []
    mono = False
    if root_ver in STATIC_VERSIONS or not root_ver:
        # monorepo 兜底：从**目标 ref** 的 packages/*/ 读包版本（本地工作区在默认分支，
        # dev 版本只在开发分支上）；按迭代日期版 > 递增号版 > 非静态 优先取
        tree = _git(repo, "ls-tree", "--name-only", f"{ref}:packages")
        for entry in [e for e in tree.splitlines() if e and not e.startswith("packages/")][:25]:
            out = _git(repo, "show", f"{ref}:packages/{entry}/package.json")
            pm = re.search(r'"version"\s*:\s*"([^"]+)"', out or "")
            if pm and pm.group(1) not in STATIC_VERSIONS:
                versions.append(pm.group(1))
                mono = True
        if len(versions) > 1:
            return _pick_version(versions), True
    return root_ver, mono


def classify(repo: Path) -> dict:
    d = {"repo": repo.name, "lang": "", "base": "", "duty": "", "sample": "",
         "confidence": "高", "flags": [], "evidence": {}}
    dates = _branch_dates(repo)
    d["evidence"]["branch_dates"] = {
        b: t for b, t in dates.items()
        if b.startswith("develop") or SPRINT_REL_RE.match(b) or b in ("master", "main")}
    sub_pkg_dirs = [p.parent.name for p in sorted(repo.glob("*/package.json"))[:5]]

    if (repo / "pom.xml").exists():
        d["lang"] = "java"
        dn_hits = [b for b in dates if DN_RE.match(b)]
        if dn_hits:
            d["base"] = max(dn_hits, key=lambda b: (dates[b], b == DEFAULT_DN_LINE, b))
            d["duty"] = "pom 版本体系（SNAPSHOT/RELEASE；bump 规则按该仓 AGENTS.md/团队约定）"
        elif dates.get("develop"):
            d["base"] = "develop"
            d["duty"] = "pom 版本体系（bump 规则按该仓 AGENTS.md/团队约定）"
        else:
            d["confidence"] = "低"
            d["flags"].append("无数字开发线，咨询操作者")
        d["sample"], _ = _read_version(repo, d["base"] or "master", sub_pkg_dirs)
        d["evidence"]["candidates"] = sorted(b for b in dates if DN_RE.match(b))
        _apply_override(d)
        return d

    if (repo / "package.json").exists():
        d["lang"] = "fe"
    elif sub_pkg_dirs:
        d["lang"] = "fe"
        d["flags"].append("package.json 在一级子目录（" + "/".join(sub_pkg_dirs[:3]) + "）")
        d["confidence"] = "中"
    else:
        d["lang"] = "?"
        d["confidence"] = "低"
        d["flags"].append("无 pom.xml / package.json，语言栈未知")

    # 候选线：develop-N（多产品线检测）+ develop-<别名> + develop + 最新 sprint release，
    # 按新近度竞速
    dn = {b: t for b, t in dates.items() if DN_RE.match(b)}
    named = {b: t for b, t in dates.items()
             if b.startswith("develop-") and not DN_RE.match(b)}
    cands = {}
    if dn:
        # 新近度竞速；日期平局（分支互 FF 到同一提交）时优先文档化默认线
        best_dn = max(dn, key=lambda b: (dn[b], b == DEFAULT_DN_LINE, b))
        cands[best_dn] = dn[best_dn]
        rest = sorted(dn, key=lambda b: dn[b], reverse=True)[1:]
        if rest:
            second = rest[0]
            try:
                gap = (date.fromisoformat(dn[best_dn]) - date.fromisoformat(dn[second])).days
                if 0 <= gap < 30:
                    d["flags"].append(f"多产品线并行：备选 {second}（{dn[second]}）距活跃线 {gap} 天，确认目标线")
                    d["confidence"] = "中"
            except ValueError:
                pass
        d["evidence"]["runner_up"] = {second: dn[second]} if rest else {}
    if named:
        best_named = max(named, key=lambda b: named[b])
        cands[best_named] = named[best_named]
    if dates.get("develop"):
        cands["develop"] = dates["develop"]
    rels = {b: t for b, t in dates.items() if SPRINT_REL_RE.match(b)}
    if rels:
        latest_rel = max(rels, key=lambda b: b)
        cands[latest_rel] = rels[latest_rel]
    d["evidence"]["candidates"] = cands

    if not cands:
        d["confidence"] = "低"
        d["flags"].append("仅 master/main 无开发线，咨询操作者")
    else:
        d["base"] = max(cands, key=lambda b: cands[b])
        losers = [f"{b}({t})" for b, t in sorted(cands.items()) if b != d["base"]]
        if losers:
            d["flags"].append("新近度破歧，落选：" + ", ".join(losers))
            d["confidence"] = "中"
        if SPRINT_REL_RE.match(d["base"] or ""):
            d["flags"].append("release 线基准：本迭代若无对应 release 分支需从主分支新切")

    if d["lang"] == "fe":
        ver, mono = _read_version(repo, d["base"] or "master", sub_pkg_dirs)
        d["sample"] = ver
        if mono:
            d["flags"].append("monorepo 子包版本")
        if DEV_SPRINT_RE.search(ver):
            d["duty"] = "迭代日期版 .N（开发/test；生产 rc/正式号）"
        elif DEV_NUM_RE.search(ver):
            d["duty"] = "递增号版（开发；生产 rc 或正式号）"
        elif not d["duty"]:
            if SPRINT_REL_RE.match(d["base"] or ""):
                d["duty"] = "无 npm 版本：版本=分支日期（CDN/部署名称）"
            elif d["base"] and (d["base"] == "develop" or d["base"].startswith("develop-")):
                d["duty"] = "无迭代版本（应用部署型，不 bump）"
            else:
                d["duty"] = "待确认"
    _apply_override(d)
    return d


def _apply_override(d: dict) -> None:
    ov = OVERRIDES.get(d["repo"])
    if not ov:
        return
    if "duty" in ov:
        d["duty"] = ov["duty"]
    d["flags"].append("覆盖表：" + ov["note"])
    d["confidence"] = "中" if d["confidence"] == "高" else d["confidence"]


def scan(src: Path, name_filter: str = "") -> list:
    name_filter = ALIASES.get(name_filter.strip().lower(), name_filter)
    repos = []
    if src.exists():
        for p in sorted(src.glob("*/*/.git")):
            if not p.is_dir() or p.parent.parent.name in EXCLUDE_NS:
                continue
            if name_filter and name_filter.lower() not in p.parent.name.lower():
                continue
            repos.append(p.parent)
    return [classify(r) for r in repos]


def main() -> int:
    ap = argparse.ArgumentParser(description="仓库家族判定（只读信号现算）")
    ap.add_argument("--repo", default="", help="仓库名子串过滤")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--src", default=str(SRC_DEFAULT), help="仓库根目录（默认 src/）")
    args = ap.parse_args()

    rows = scan(Path(args.src), args.repo)
    if not rows:
        print(f"未匹配到仓库（src={args.src}, filter={args.repo!r}）", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    hdr = f"{'仓库':<30} {'栈':<5} {'基准分支(活跃线)':<24} {'版本职责':<44} {'置信':<4} 旗标"
    print(hdr)
    print("-" * 130)
    for d in rows:
        flags = "；".join(d["flags"]) or "-"
        print(f"{d['repo']:<30} {d['lang']:<5} {d['base'] or '?':<24} {d['duty']:<44} "
              f"{d['confidence']:<4} {flags}")
        if d["sample"]:
            print(f"{'':<30} 样例版本: {d['sample']}")
    stat = {c: sum(1 for r in rows if r["confidence"] == c) for c in ("高", "中", "低")}
    print(f"\n共 {len(rows)} 仓；置信 高={stat['高']} 中={stat['中']} 低={stat['低']}"
          f"（中/低含旗标 → 开工时与操作者确认）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
