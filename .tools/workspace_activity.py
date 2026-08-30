# -*- coding: utf-8 -*-
"""工作区活动统计（本仓 git log，只读）。

统计本工作区仓的协作活动：总提交数、时间跨度、逐月提交、顶层目录分布——
供阶段回顾 / 协作节奏复盘复算与留档，替代「AI 会话内手工取 git log」的
非规格化做法。

口径：HEAD 全历史、--date=short 的提交日期；顶层目录 = 路径首段（根文件计 <root>）。

用法：

  python .tools/workspace_activity.py             # 打印摘要
  python .tools/workspace_activity.py --write     # 另存 json 到 temp/（用完即清，留档自移）

零第三方依赖（stdlib + git 命令）；不含个人数据 hardcode，仓路径按相对本仓定位。
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "temp"


def git(*args):
    r = subprocess.run(["git", "-C", str(REPO_ROOT), *args],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit(f"error: git {' '.join(args)} 失败：{r.stderr.strip()}")
    return r.stdout


def collect():
    dates = git("log", "--format=%ad", "--date=short").split()
    monthly = Counter(d[:7] for d in dates)
    paths = [line for line in git("log", "--name-only", "--format=").splitlines() if line]
    top_dirs = Counter(p.replace("\\", "/").split("/")[0] if "/" in p else "<root>"
                       for p in paths)
    return {
        "total": len(dates),
        "span": {"first": min(dates), "last": max(dates)},
        "monthly": dict(sorted(monthly.items())),
        "top_dirs": dict(top_dirs.most_common(10)),
        "collected-at": date.today().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="工作区活动统计（本仓 git log）")
    parser.add_argument("--write", action="store_true",
                        help="另存 json 到 temp/workspace-activity.json（用完即清）")
    args = parser.parse_args()

    data = collect()
    print(f"# 工作区活动（{data['span']['first']} ~ {data['span']['last']}，采集 {data['collected-at']}）")
    print(f"- 总提交：{data['total']}")
    print("- 逐月：" + "; ".join(f"{m}={c}" for m, c in data["monthly"].items()))
    print("- 顶层目录 top10：" + "; ".join(f"{d}={c}" for d, c in data["top_dirs"].items()))
    if args.write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / "workspace-activity.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(f"已写入：{out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
