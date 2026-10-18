#!/usr/bin/env python3
"""exp-lookup：exps 错误驱动检索（再犯现场的发现引擎）。

机制真源 = WORKFLOW §2.4「错误驱动召回」：命令失败/异常输出出现时，先拿错误
特征词跑本工具再深查根因——命中即用 + 记 exps/TRIGGERS.md 疑似候选；零命中
≠ 无相关条目——先以同特征词查 notes/INDEX.md（判型收编后知识常驻 notes），
双库零命中才是 INDEX 缺词信号（反哺该条关键词的现象词轴）。

用法：
  python .tools/exp-lookup.py "Cannot find package 'xxx'"
  python .tools/exp-lookup.py --file err.txt --scene build
  some-command 2>&1 | python .tools/exp-lookup.py -
  python .tools/exp-lookup.py --self-test        # 真值对数（已知查询必中已知条目）

只读、零第三方依赖；检索面 = exps/INDEX.md 热层（标题/摘要/关键词/场景列）。
"""

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

INDEX_PATH = Path(__file__).resolve().parent.parent / "exps" / "INDEX.md"

# 噪声词：错误文本高频但无判别力（形态普查：错误族实测提取后过滤）
STOPWORDS = {
    "error", "errors", "failed", "failure", "fatal", "warn", "warning",
    "cannot", "could", "found", "file", "files", "line", "code", "stack",
    "trace", "at", "the", "and", "for", "with", "node_modules", "command",
    "something", "went", "wrong", "please", "check", "true", "false",
}

CJK = re.compile(r"[\u4e00-\u9fff]+")


def extract_features(text: str) -> set[str]:
    """从错误输出/主题词提取特征：错误码、引号串、包名、英文实词、CJK 词。"""
    feats: set[str] = set()
    low = text.lower()
    # 错误码 / 下划线常量（ERR_MODULE_NOT_FOUND、lockfileVersion 不截，保整词）
    feats.update(m.group(0).lower() for m in re.finditer(r"[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+", low))
    # 引号内串（报错里最常携带判别信息：包名、路径尾、配置名）
    feats.update(m.group(1).lower() for m in re.finditer(r"'([^'\n]{2,80})'", low))
    # 域名式包名 @scope/pkg
    feats.update(m.group(0).lower() for m in re.finditer(r"@[a-z0-9-]+/[a-z0-9.-]+", low))
    # 英文实词（≥4 字符，去噪）
    for w in re.findall(r"[a-z][a-z0-9.-]{3,}", low):
        if w not in STOPWORDS and not w.isdigit():
            feats.add(w)
    # CJK 连续段（成词直接用，长段再切 2-gram）
    for run in CJK.findall(text):
        feats.add(run)
        feats.update(run[i : i + 2] for i in range(len(run) - 1))
    return feats


def parse_index() -> list[dict]:
    rows: list[dict] = []
    for line in INDEX_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in re.split(r"(?<!\\)\|", line)]
        if len(cols) < 7 or cols[1] in ("标题", "") or set(cols[2]) <= {"-", " "}:
            continue
        rows.append(
            {
                "title": cols[1],
                "summary": cols[2],
                "keywords": [k.strip().lower() for k in cols[3].split(",") if k.strip()],
                "scene": cols[4],
                "file": cols[5],
            }
        )
    return rows


def index_health() -> str | None:
    """解析统计自检：撕裂行（列数不足被跳过 → 检索面变窄）与粘连行（列数超限错位解析）。"""
    lines = [l for l in INDEX_PATH.read_text(encoding="utf-8").splitlines() if l.startswith("|")]
    n_table = len(lines)
    n_parsed = len(parse_index())
    drift = n_table - n_parsed - 2  # 表头 + 分隔行；>0 = 有行被跳过（撕裂/列数异常）
    oversized = sum(1 for l in lines if len(re.split(r"(?<!\\)\|", l)) > 8)
    problems = []
    if drift:
        problems.append(f"表行 {n_table} 但解析 {n_parsed} 条（差 {drift}，疑撕裂/列数不足行被跳过）")
    if oversized:
        problems.append(f"{oversized} 行列数超限（疑多行粘连挤一行，错位解析）")
    if problems:
        return "INDEX 表结构异常：" + "；".join(problems) + "——kbindex 机检分区（后批接入）落地前，先按行格式注释人工核对表行"
    return None


def score_row(feats: set[str], row: dict) -> int:
    s = 0
    blob_kw = " ".join(row["keywords"])
    blob_sum = row["summary"].lower()
    blob_title = row["title"].lower()
    for f in feats:
        if len(f) < 2:
            continue
        if any(f in k or k in f for k in row["keywords"]):
            s += 3
        elif f in blob_kw:
            s += 3
        elif f in blob_sum:
            s += 2
        elif f in blob_title:
            s += 1
    return s


def lookup(query: str, scene: str = "", top: int = 8) -> list[tuple[int, dict]]:
    feats = extract_features(query)
    if not feats:
        # 短词查询兜底（如裸查 nvm）：直接用原词当特征，防「零命中」把在册条目误报为缺词
        feats = {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9-]+", query)
                 if len(w) >= 2 and w.lower() not in STOPWORDS}
    if not feats:
        return []
    scored = []
    for row in parse_index():
        if scene and scene.lower() not in row["scene"].lower():
            continue
        s = score_row(feats, row)
        if s > 0:
            scored.append((s, row))
    scored.sort(key=lambda x: (-x[0], x[1]["file"]))
    return scored[:top]


def main() -> int:
    ap = argparse.ArgumentParser(description="exps 错误驱动检索（错误驱动召回发现引擎）")
    ap.add_argument("query", nargs="*", help="错误输出/主题词（或 --file / - 读 stdin）")
    ap.add_argument("--file", help="从文件读查询文本（- = stdin）")
    ap.add_argument("--scene", default="", help="按场景列过滤（build/install/release/migrate/push 开放集）")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--self-test", action="store_true", help="真值对数：已知查询必中已知条目")
    args = ap.parse_args()

    if args.self_test:
        cases = [
            ("markdownlint 批量变换 围栏 闭合 错位", {"workflow/paired-structure-batch-transform.md"}),
            ("vendor 上游 lock hash 比对 漂移", {"workflow/vendor-upstream-compare-early.md"}),
            ("截图 html png browser-use IAB 信息图", {"tooling/zcode-browser-use-screenshot-html.md"}),
        ]
        if not parse_index():
            print("[SKIP] exps/INDEX.md 无数据行（模板态空表）——真值对为源仓条目，模板态跳过，仅解析自检")
            cases = []
        ok = True
        for q, expect in cases:
            hits = {r["file"] for _, r in lookup(q)}
            hit = hits & expect
            print(f"[{'PASS' if hit else 'FAIL'}] {q[:40]!r} -> {sorted(hits) or '零命中'}")
            ok &= bool(hit)
        health = index_health()
        print(f"[{'PASS' if health is None else 'FAIL'}] INDEX 解析统计自检 -> {health or '表行/解析数一致'}")
        ok &= health is None
        return 0 if ok else 1

    if args.file == "-":
        text = sys.stdin.read()
    elif args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="replace")
    else:
        text = " ".join(args.query)
    if not text.strip():
        print("用法：python .tools/exp-lookup.py \"<错误输出或主题词>\"（详见 --help）", file=sys.stderr)
        return 2

    health = index_health()
    if health:
        print(health)
    results = lookup(text, scene=args.scene, top=args.top)
    if not results:
        print("零命中（≠ 无相关条目——先以同特征词查 notes/INDEX.md，判型收编后知识常驻 notes；双库零命中才是 INDEX 缺词信号：确认无既有可并后，把本次现象词反哺相关条目关键词或新条目）")
        return 1
    print(f"命中 {len(results)} 条（按相关度）：")
    for s, r in results:
        tag = f"〔场景 {r['scene']}〕" if r["scene"] else ""
        print(f"  [{s:3d}] {tag}{r['title']}")
        print(f"        {r['file']}")
    print(f"[stats] INDEX 表行 {len([l for l in INDEX_PATH.read_text(encoding='utf-8').splitlines() if l.startswith('|')])}，解析 {len(parse_index())} 条")
    print("命中后动作：读条目正文对照根因判同类 → 同类记 exps/TRIGGERS.md 疑似候选行（WORKFLOW §2.4 错误驱动召回）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
