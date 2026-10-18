#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rollout-extract.py — ZCode 会话原文提取器（自评/评审一手证据源）

从 ~/.zcode/cli/rollout/ 的 model-io-sess_*.jsonl 抽取**对话正文**（Markdown 转录），
供自评 / 评审等场景做「会话原文直读」——台账类自写材料只作导航，一手证据
以本工具转录 + commit + 产物原文为准。

数据源要点（ZCode 特有，路径/格式变动时本脚本报错即修）：
- 每行 = 一次模型调用记录：request.messages 是当时上下文的消息**尾窗**（≤64 条），
  request.messageOffset 是窗内首条消息的全局索引 → 跨行按 offset 拼接去重。
- 文件内消息流并非单一序：上下文压缩后续写 offset 归零（新纪元）、旁路小窗穿插
  → 按「链」组织：精确续接（chain 末尾 == 记录起点）优先、覆盖窗次之、否则开新链；
  消息最多的链 = 主链。subAgent 调用落独立文件（文件名含 _subagent_），不混入。
- 滚动覆盖：早期消息滚出窗口后不再可恢复，转录头部声明覆盖边界，窗外轮次以
  commit/任务档案补证。

用法：
  rollout-extract.py --list                      # 列 rollout 文件（标注主会话/subAgent/大小/mtime）
  rollout-extract.py --latest --stats            # 最新主会话的分链统计（默认无 --out 时即统计）
  rollout-extract.py --latest --out temp/<任务id>/session.md   # 主链转录写文件
  rollout-extract.py --rollout <file> --out <md> [--all-chains] [--with-reasoning] [--with-tool-results]
  同参数 --json 时 stdout 只出纯 JSON（进度/告警走 stderr）

消息分类：injected（system 注入）/ user-real（真人话，剥离 <system-reminder> 块后
非空）/ user-reminder / assistant（文本块；toolCalls 记一行调用注记）/ reasoning
（默认略，--with-reasoning 含）/ tool-result（默认略，--with-tool-results 含）。
转录含会话原文（可能含敏感内容），输出路径自担、勿外传。
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROLLOUT_DIR = os.environ.get("ROLLOUT_DIR") or os.path.join(os.path.expanduser("~"), ".zcode", "cli", "rollout")
SUBAGENT_MARK = "_subagent_"
REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)
MAX_WINDOW = 64  # 尾窗上限，超出视为数据异常仅告警


def find_rollout_files():
    files = glob.glob(os.path.join(ROLLOUT_DIR, "model-io-sess_*.jsonl"))
    return sorted(files, key=os.path.getmtime, reverse=True)


def is_subagent(path):
    return SUBAGENT_MARK in os.path.basename(path)


def load_records(path):
    """逐行解析，返回 [{offset, msgs, time}]；无消息窗的行跳过。"""
    records = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                print(f"[warn] 第 {lineno} 行非 JSON，已跳过（长度 {len(line)}，不打印内容防外泄）", file=sys.stderr)
                continue
            req = rec.get("request") or {}
            msgs = (req.get("body") or {}).get("messages") or req.get("messages") or []
            if not msgs:
                continue
            records.append({
                "offset": req.get("messageOffset") or 0,
                "msgs": msgs,
                "time": (rec.get("completedAt") or "")[:19],
            })
    return records


class Chain:
    """一段连续 offset 空间的消息流（主链或压缩后新纪元/旁路窗）。"""

    def __init__(self):
        self.msgs = {}       # 全局 offset -> (msg, first_seen_time)
        self.min_off = None
        self.max_end = None  # 排他上界

    def absorb(self, rec):
        off, msgs, t = rec["offset"], rec["msgs"], rec["time"]
        for i, m in enumerate(msgs):
            g = off + i
            if g not in self.msgs:
                self.msgs[g] = (m, t)
        lo, hi = off, off + len(msgs)
        self.min_off = lo if self.min_off is None else min(self.min_off, lo)
        self.max_end = hi if self.max_end is None else max(self.max_end, hi)

    def covers(self, off):
        return self.min_off is not None and self.min_off <= off < self.max_end


def _sig(m):
    """消息指纹（role + content + 工具调用名）：同 offset 跨记录同流应一致，不一致 = 撞号。"""
    return (m.get("role"), json.dumps(m.get("content"), sort_keys=True, ensure_ascii=False),
            tuple(t.get("name") for t in m.get("toolCalls") or [] if isinstance(t, dict)))


def _compatible(chain, off, msgs):
    """记录窗与链重叠段同 offset 必须同内容；冲突（如压缩后归零撞短会话原链）则非同流。"""
    for i, m in enumerate(msgs):
        g = off + i
        if g in chain.msgs and _sig(chain.msgs[g][0]) != _sig(m):
            return False
    return True


def build_chains(records):
    chains = []
    for rec in records:
        off = rec["offset"]
        exact = [c for c in chains if c.max_end == off and _compatible(c, off, rec["msgs"])]
        cand = exact[0] if exact else None                              # 精确续接
        if cand is None:
            covering = [c for c in chains if c.covers(off) and _compatible(c, off, rec["msgs"])]
            cand = max(covering, key=lambda c: c.max_end) if covering else None  # 覆盖窗
        if cand is None:
            cand = Chain()
            chains.append(cand)
        cand.absorb(rec)
        if len(rec["msgs"]) > MAX_WINDOW:
            print(f"[warn] 窗 {len(rec['msgs'])} 条超上限 {MAX_WINDOW}，数据形态可能已变", file=sys.stderr)
    return chains


def blocks(msg):
    """消息 content 归一为 [(类型, 文本)]；字符串视作单个 text 块。"""
    c = msg.get("content")
    if isinstance(c, str):
        return [("text", c)]
    if isinstance(c, list):
        out = []
        for b in c:
            if isinstance(b, dict) and b.get("type"):
                out.append((b["type"], b.get("text") or ""))
        return out
    return []


def classify(msg):
    """返回 (类别, 干净文本, toolCalls)；类别 ∈ injected/user-real/user-reminder/assistant/reasoning/tool-result。"""
    role = msg.get("role")
    calls = [t.get("name", "?") for t in (msg.get("toolCalls") or []) if isinstance(t, dict)]
    if role == "system":
        return "injected", "", []
    if role == "tool":
        return "tool-result", "".join(t for k, t in blocks(msg) if k == "text"), []
    if role == "user":
        raw = "".join(t for k, t in blocks(msg) if k == "text")
        clean = REMINDER_RE.sub("", raw).strip()
        return ("user-real", clean, []) if clean else ("user-reminder", raw, [])
    if role == "assistant":
        text = "\n\n".join(t for k, t in blocks(msg) if k == "text" and t.strip())
        reasoning = "".join(t for k, t in blocks(msg) if k == "reasoning")
        if text.strip() or calls:
            return "assistant", text.strip(), calls
        if reasoning.strip():
            return "reasoning", reasoning.strip(), []
        return "assistant", "", calls
    return role or "unknown", "", []


def chain_stats(chain):
    from collections import Counter
    counts = Counter()
    for _, (m, _) in sorted(chain.msgs.items()):
        counts[classify(m)[0]] += 1
    times = [t for _, (_, t) in chain.msgs.items() if t]
    return {
        "offset_range": [chain.min_off, chain.max_end],
        "messages": len(chain.msgs),
        "breakdown": dict(counts),
        "user_real_texts": counts.get("user-real", 0),
        "time_range": [min(times) if times else "", max(times) if times else ""],
    }


def render_transcript(chain, path, opts):
    st = chain_stats(chain)
    lines = [
        f"# 会话转录（主链）",
        "",
        f"- 来源：`{os.path.basename(path)}`",
        f"- 全局 offset：[{st['offset_range'][0]}, {st['offset_range'][1]})，共 {st['messages']} 条消息",
        f"- 分类：真人 {st['breakdown'].get('user-real', 0)} / assistant {st['breakdown'].get('assistant', 0)}"
        f" / 注入 {st['breakdown'].get('injected', 0)} / 工具结果 {st['breakdown'].get('tool-result', 0)}",
        f"- 时间（首条入窗 → 最后记录）：{st['time_range'][0]} → {st['time_range'][1]}",
        f"- **覆盖边界**：本转录只含滚动窗口内消息，更早轮次已滚出——以 commit/任务档案补证，引用时声明此边界。",
        "",
    ]
    for g, (m, t) in sorted(chain.msgs.items()):
        kind, text, calls = classify(m)
        if kind == "injected":
            lines.append(f"### [{g}] injected（{sum(len(x) for _, x in blocks(m))} 字，略）")
            lines.append("")
            continue
        if kind == "user-reminder":
            lines.append(f"### [{g}] user-reminder（系统注入提醒，略）")
            lines.append("")
            continue
        if kind == "tool-result" and not opts["with_tool_results"]:
            continue
        if kind == "reasoning" and not opts["with_reasoning"]:
            continue
        label = {"user-real": "user（真人）", "assistant": "assistant", "tool-result": "tool-result",
                 "reasoning": "assistant（reasoning）"}.get(kind, kind)
        head = f"### [{g}] {label}（{len(text)} 字，{t}）"
        if calls:
            head += f" [调用工具: {', '.join(calls)}]"
        lines.append(head)
        lines.append("")
        if text:
            lines.append("````text")
            lines.append(text)
            lines.append("````")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="ZCode 会话原文提取器（rollout → Markdown 转录）")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--rollout", help="指定 rollout jsonl 路径")
    src.add_argument("--latest", action="store_true", help="最新主会话文件（排除 subAgent 文件）")
    src.add_argument("--list", action="store_true", help="列出 rollout 文件")
    ap.add_argument("--out", help="转录输出路径（缺省只出统计）")
    ap.add_argument("--all-chains", action="store_true", help="转录含全部链（缺省只主链）")
    ap.add_argument("--with-reasoning", action="store_true", help="含 reasoning 块")
    ap.add_argument("--with-tool-results", action="store_true", help="含工具结果正文")
    ap.add_argument("--json", action="store_true", help="stdout 纯 JSON（统计口径）")
    opts_flags = {"with_reasoning": None, "with_tool_results": None}
    args = ap.parse_args()
    if not (args.rollout or args.latest or args.list):
        ap.error("需显式三选一：--list / --latest / --rollout <路径>（无参不动作，防误触发读外部路径）")

    files = find_rollout_files()
    if args.list or not files:
        rows = [{
            "file": os.path.basename(f), "subagent": is_subagent(f),
            "size_mb": round(os.path.getsize(f) / 1e6, 1), "mtime": datetime.fromtimestamp(os.path.getmtime(f)).isoformat(timespec="minutes"),
        } for f in files]
        if args.json:
            print(json.dumps({"files": rows}, ensure_ascii=False))
        else:
            print("rollout 文件（新→旧）：")
            for r in rows:
                print(f"  {'[subAgent]' if r['subagent'] else '[主会话]'} {r['file']}  {r['size_mb']}MB  {r['mtime']}")
        if not files:
            print(f"未找到 rollout 文件：{ROLLOUT_DIR}（ZCode 路径变化时须修 ROLLOUT_DIR）", file=sys.stderr)
            return 1
        return 0

    if args.rollout:
        path = args.rollout
    else:  # --latest（无参已在入口拦截）
        main_files = [f for f in files if not is_subagent(f)]
        if not main_files:
            print("无主会话 rollout 文件", file=sys.stderr)
            return 1
        path = main_files[0]
        print(f"[info] 选定最新主会话：{os.path.basename(path)}", file=sys.stderr)

    records = load_records(path)
    chains = sorted(build_chains(records), key=lambda c: -len(c.msgs))
    if not chains:
        print("文件内无消息窗记录", file=sys.stderr)
        return 1
    stats = {"file": os.path.basename(path), "records": len(records), "chains": [chain_stats(c) for c in chains]}
    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    elif not args.out:
        print(f"文件 {os.path.basename(path)}：{len(records)} 条记录 → {len(chains)} 条链")
        for i, c in enumerate(chains):
            s = chain_stats(c)
            mark = "（主链）" if i == 0 else ""
            print(f"  链{i}{mark} offset {s['offset_range']}  {s['messages']} 消息  真人 {s['user_real_texts']}  {s['time_range'][0]} → {s['time_range'][1]}")
        print("（--out <file.md> 出转录；--json 出机读统计）")
    if args.out:
        opts_flags.update(with_reasoning=args.with_reasoning, with_tool_results=args.with_tool_results)
        picked = chains if args.all_chains else chains[:1]
        parts = [render_transcript(c, path, opts_flags) if i == 0 else
                 render_transcript(c, path, opts_flags).replace("# 会话转录（主链）", f"# 会话转录（链 {i}）")
                 for i, c in enumerate(picked)]
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write("\n\n---\n\n".join(parts))
        s = chain_stats(chains[0])
        print(f"[info] 转录已写 {args.out}（主链 {s['messages']} 条 / 真人 {s['user_real_texts']} 条）", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
