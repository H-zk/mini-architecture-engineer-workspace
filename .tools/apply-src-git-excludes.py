#!/usr/bin/env python3
"""统一铺装 src/ 各仓 git 本地忽略（.git/info/exclude 托管块）。

真源 = 同目录 src-git-excludes.txt；对 src/ 下全部 git 仓幂等铺装/回收托管块。
边界：.worktrees/ 下的仓不动（worktree 非独立仓）；只读参照类克隆（同事库参照等，
如有）不宜写入，按需加入 SKIP_PARTS。不写 core.excludesFile——repo 级该配置会
遮蔽用户全局 ~/.config/git/ignore，托管块与其叠加生效。
"""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
EXCLUDES_SRC = Path(__file__).resolve().parent / "src-git-excludes.txt"
BEGIN = "# >>> workspace-managed excludes (真源 .tools/src-git-excludes.txt)"
END = "# <<< workspace-managed excludes"
SKIP_PARTS = {".worktrees"}


def patterns():
    lines = [l.strip() for l in EXCLUDES_SRC.read_text(encoding="utf-8").splitlines()]
    return [l for l in lines if l and not l.startswith("#")]


def iter_repos():
    # 深度自 2 起：基础副本按 AGENTS「代码视图隔离」约定为 src/<namespace>/<repo> 两层；
    # 一层直挂仓（src/<repo>）不符约定、静默不扫，如需支持再放宽起点
    for depth in (2, 3, 4, 5):
        for g in SRC.glob("/".join(["*"] * depth + [".git"])):
            if g.is_dir() and not SKIP_PARTS & set(g.parts):
                yield g.parent


def apply(repo: Path, pats: list[str]):
    excl = repo / ".git" / "info" / "exclude"
    excl.parent.mkdir(parents=True, exist_ok=True)
    old = excl.read_text(encoding="utf-8") if excl.exists() else ""
    # 去掉旧托管块（含可能的历史裸行残留不做处理——只管自己写过的）
    stripped = re.sub(
        re.escape(BEGIN) + r"\n.*?" + re.escape(END) + r"\n?", "", old, flags=re.S
    )
    block = BEGIN + "\n" + "\n".join(pats) + "\n" + END + "\n" if pats else ""
    new = (stripped.rstrip("\n") + "\n\n" + block if stripped.strip() else block)
    if new != old:
        excl.write_text(new, encoding="utf-8", newline="")
        return "written"
    return "ok"


def main():
    pats = patterns()
    if not pats:
        print("真源为空——不铺装新忽略项，仅回收既有托管块（如有）")
    counts = {"written": 0, "ok": 0}
    for repo in sorted(iter_repos()):
        counts[apply(repo, pats)] += 1
    print(f"铺装完成：{sum(counts.values())} 仓"
          f"（新写 {counts['written']} / 已一致 {counts['ok']}）；忽略项 {pats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
