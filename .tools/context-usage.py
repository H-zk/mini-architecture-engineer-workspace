#!/usr/bin/env python3
"""ZCode 会话上下文占用探针（只读）。

读 ~/.zcode/cli/rollout/ 主会话的 model-io 流水（model-io-sess_*.jsonl），抽 usage
字段报告真实上下文占用与逐调用增长轨迹；--breakdown 附底座归因粗估。

口径与红线：
- 真实 ctx = 归一化 inputTokens（**已含** cacheReadTokens，两者再相加即双计——首测踩过）；
  归一化字段缺失时回退 Anthropic 式 input_tokens + cache_read/creation 相加。
- 只读、只抽 usage 与长度字段，不打印任何会话正文（--breakdown 体积估算需按消息体计数，内容不外显——测量不得成为泄漏源/膨胀源）。
- ZCode 特有数据源（工具无关边界）：rollout 路径变化或换工具时本脚本自然失效，报错即修。

用法：
  python .tools/context-usage.py                # 最新主会话（≈当前会话）占用 + 轨迹
  python .tools/context-usage.py --breakdown    # 附底座归因粗估（system/工具/消息）
  python .tools/context-usage.py --list         # 列最近主会话文件（多会话并行时核对）
  python .tools/context-usage.py --session fed9f942  # 按 sessionId 前缀定位
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

ROLLOUT_DIR = os.path.join(os.path.expanduser("~"), ".zcode", "cli", "rollout")


def find_files():
    files = [
        f for f in glob.glob(os.path.join(ROLLOUT_DIR, "model-io-sess_*.jsonl"))
        if "subagent" not in os.path.basename(f)  # 子代理流水不含主窗口占用
    ]
    files.sort(key=os.path.getmtime, reverse=True)
    return files


def usage_of(rec):
    u = (rec.get("response") or {}).get("usage") or {}
    ctx = u.get("inputTokens")
    if ctx is None:
        ctx = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
               + u.get("cache_creation_input_tokens", 0))
    cache = u.get("cacheReadTokens", u.get("cache_read_input_tokens", 0)) or 0
    out = u.get("outputTokens", u.get("output_tokens", 0)) or 0
    return ctx, cache, out


def parse_records(path):
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue  # 尾部半行（写入中）
            ctx, cache, out = usage_of(rec)
            if not ctx:
                continue
            records.append((rec.get("startedAt", "?"), ctx, cache, out, rec))
    return records


def approx_tokens(obj):
    try:
        return len(json.dumps(obj, ensure_ascii=False)) // 3  # 中英混合粗口径
    except (TypeError, ValueError):
        return 0


def breakdown(rec):
    body = ((rec.get("request") or {}).get("body")) or (rec.get("request") or {}) or {}
    msgs = body.get("messages") or (rec.get("request") or {}).get("messages") or []
    return [
        ("system（系统提示+工作区注入）", approx_tokens(body.get("system"))),
        ("tools（工具定义）", approx_tokens(body.get("tools"))),
        ("messages（会话正文）", approx_tokens(msgs)),
    ]


def main():
    ap = argparse.ArgumentParser(description="ZCode 会话上下文占用探针（只读）")
    ap.add_argument("--list", action="store_true", help="列最近主会话文件后退出")
    ap.add_argument("--session", help="按 sessionId（文件名前缀/子串）定位目标会话")
    ap.add_argument("--file", help="显式指定 model-io jsonl 路径")
    ap.add_argument("--breakdown", action="store_true", help="附底座归因粗估")
    ap.add_argument("--tail", type=int, default=10, help="轨迹显示最近 N 次调用")
    args = ap.parse_args()
    if args.tail < 1:
        ap.error("--tail 须为正整数（records[-0:] 会退化为全量打印）")

    files = find_files()
    if not files:
        sys.exit(f"未找到 rollout 文件：{ROLLOUT_DIR}（ZCode 路径变化时须修 ROLLOUT_DIR）")

    if args.list:
        for f in files[:10]:
            stamp = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%m-%d %H:%M")
            print(f"{stamp}  {os.path.getsize(f) // 1024:>6}KB  {os.path.basename(f)}")
        return

    if args.file:
        target = args.file
    elif args.session:
        hits = [f for f in files if args.session in os.path.basename(f)]
        if len(hits) != 1:
            sys.exit(f"--session {args.session!r} 命中 {len(hits)} 个文件，请用 --list 核对")
        target = hits[0]
    else:
        target = files[0]  # 最新 mtime 的主会话 ≈ 当前会话；多会话并行时用 --list 核对

    records = parse_records(target)
    if not records:
        sys.exit(f"无可用 usage 记录：{target}")

    started, ctx, cache, out, raw = records[-1]
    model = ((raw.get("model") or {}).get("modelId", "?"))
    share = cache / ctx if ctx else 0
    print(f"目标会话: {os.path.basename(target)}")
    print(f"模型: {model}   模型调用数: {len(records)}（尾部半行自动跳过）")
    print(f"最新占用: ctx_in={ctx:,}  缓存读占 {share:.0%}  该调用输出 {out:,}")
    shown = records[-args.tail:]
    start_idx = len(records) - len(shown) + 1
    print(f"轨迹（最近 {len(shown)} 次调用，ctx_in 逐调用）:")
    for i, (t, c, _, o, _) in enumerate(shown, start_idx):
        print(f"  #{i:<3} {(t or '?')[11:19]}  ctx_in={c:,}  out={o:,}")

    if args.breakdown:
        print("底座归因（最近一次调用请求体字符折算 /3，粗估仅供量级）:")
        for name, val in breakdown(raw):
            print(f"  {name}: ~{val:,} tok")
        print("  注：system 含工作区 AGENTS.md 注入；skills 描述并入 system/tools，无法精确切分")


if __name__ == "__main__":
    main()
