"""graphify 建图驱动：复刻上游 skill.md（v8，graphifyy@0.9.67）编排的代码仓快速路径。

用法（经本目录 uv 工程运行，graphifyy 版本随 uv.lock 钉死）：
    uv run --project .tools/graphify python .tools/graphify/build.py <目标仓根>

流水线：detect → AST 结构抽取（零 LLM）→ 空语义文件（code-only 快速路径）→ 合并 →
建图 + 聚类 + 报告。产物落 <目标仓根>/graphify-out/（graph.json / GRAPH_REPORT.md /
状态件，属工具产物，进 src-git-excludes 统一本地忽略）。查询面走 graphify CLI
（god-nodes / path --undirected / explain），用法与坑见 .tools/graphify.md。
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: uv run --project .tools/graphify python .tools/graphify/build.py <目标仓根>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"目标目录不存在: {root}", file=sys.stderr)
        return 2

    out = root / "graphify-out"
    out.mkdir(exist_ok=True)
    (out / ".graphify_python").write_text(sys.executable, encoding="utf-8")
    (out / ".graphify_root").write_text(str(root), encoding="utf-8")

    from graphify.detect import detect

    result = detect(root)
    (out / ".graphify_detect.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    print(f"Detected {result['total_files']} files · ~{result.get('total_words', 0)} words")
    for cat in ("code", "document", "paper", "image", "video"):
        n = len(result.get("files", {}).get(cat, []))
        if n:
            print(f"  {cat}: {n} files")
    if result.get("skipped_sensitive"):
        print(f"  skipped_sensitive: {result['skipped_sensitive']}")

    from graphify.extract import collect_files, extract

    code_files = []
    for f in result.get("files", {}).get("code", []):
        p = Path(f)
        code_files.extend(collect_files(p) if p.is_dir() else [p])
    if code_files:
        ast_result = extract(code_files, cache_root=root)
        (out / ".graphify_ast.json").write_text(
            json.dumps(ast_result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"AST: {len(ast_result['nodes'])} nodes, {len(ast_result['edges'])} edges")
    else:
        (out / ".graphify_ast.json").write_text(
            json.dumps({"nodes": [], "edges": [], "input_tokens": 0, "output_tokens": 0}),
            encoding="utf-8",
        )
        print("No code files - skipping AST extraction")

    # code-only 快速路径：空语义文件（语义层默认不启用，见 .tools/graphify.md 红线节）
    (out / ".graphify_semantic.json").write_text(
        json.dumps({"nodes": [], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}),
        encoding="utf-8",
    )

    ast = json.loads((out / ".graphify_ast.json").read_text(encoding="utf-8"))
    sem = json.loads((out / ".graphify_semantic.json").read_text(encoding="utf-8"))
    seen = {n["id"] for n in ast["nodes"]}
    merged_nodes = list(ast["nodes"])
    for n in sem["nodes"]:
        if n["id"] not in seen:
            merged_nodes.append(n)
    merged = {
        "nodes": merged_nodes,
        "edges": ast["edges"] + sem["edges"],
        "hyperedges": sem.get("hyperedges", []),
        "input_tokens": sem.get("input_tokens", 0),
        "output_tokens": sem.get("output_tokens", 0),
    }
    (out / ".graphify_extract.json").write_text(
        json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Merged: {len(merged_nodes)} nodes ({len(ast['nodes'])} AST + {len(sem['nodes'])} semantic)")

    from graphify.analyze import god_nodes, suggest_questions, surprising_connections
    from graphify.build import build_from_json
    from graphify.cluster import cluster, score_all
    from graphify.export import to_json
    from graphify.report import generate

    g = build_from_json(merged, root=str(root), directed=False)
    if g.number_of_nodes() == 0:
        print("ERROR: Graph is empty - extraction produced no nodes.")
        return 1
    communities = cluster(g)
    cohesion = score_all(g, communities)
    gods = god_nodes(g)
    surprises = surprising_connections(g, communities)
    labels = {cid: "Community " + str(cid) for cid in communities}
    questions = suggest_questions(g, communities, labels)
    to_json(g, communities, str(out / "graph.json"))
    report = generate(
        g,
        communities,
        cohesion,
        labels,
        gods,
        surprises,
        result,
        {"input": merged.get("input_tokens", 0), "output": merged.get("output_tokens", 0)},
        str(root),
        suggested_questions=questions,
    )
    (out / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    analysis = {
        "communities": {str(k): v for k, v in communities.items()},
        "cohesion": {str(k): v for k, v in cohesion.items()},
        "gods": gods,
        "surprises": surprises,
        "questions": questions,
    }
    (out / ".graphify_analysis.json").write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Graph: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges, {len(communities)} communities")
    print(f"god-nodes top5: {[x if isinstance(x, str) else x.get('label', x) for x in gods[:5]]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
