"""Trim a JSON background graph to an exact average degree and degree cap."""

import argparse
import json
import random
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", type=Path)
    parser.add_argument("--average-degree", type=float, default=3.0)
    parser.add_argument("--max-degree", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--backup-suffix", default=".before_degree_trim")
    args = parser.parse_args()

    data = json.loads(args.graph.read_text())
    node_ids = [node["id"] for node in data["nodes"]]
    target_edges_float = len(node_ids) * args.average_degree / 2
    target_edges = round(target_edges_float)
    if abs(target_edges - target_edges_float) > 1e-9:
        raise ValueError("Requested average degree does not produce an integer edge count")

    edges = list(data["links"])
    random.Random(args.seed).shuffle(edges)
    degrees = {node_id: 0 for node_id in node_ids}
    selected = []
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        if degrees[source] >= args.max_degree or degrees[target] >= args.max_degree:
            continue
        selected.append(edge)
        degrees[source] += 1
        degrees[target] += 1
        if len(selected) == target_edges:
            break

    if len(selected) != target_edges:
        raise RuntimeError(
            f"Could retain only {len(selected)} of {target_edges} required edges "
            f"with max degree {args.max_degree}"
        )

    backup = args.graph.with_name(args.graph.name + args.backup_suffix)
    if not backup.exists():
        shutil.copy2(args.graph, backup)

    data["links"] = selected
    args.graph.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Backup: {backup}")
    print(f"Vertices: {len(node_ids)}")
    print(f"Edges: {len(selected)}")
    print(f"Average degree: {2 * len(selected) / len(node_ids):.6f}")
    print(f"Maximum degree: {max(degrees.values())}")


if __name__ == "__main__":
    main()
