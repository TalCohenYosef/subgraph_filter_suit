import json
import random
from pathlib import Path

SEED = 42
N_QUERIES = 1000

random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent


def generate_gnp_edges(n, p):
    edges = []

    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < p:
                edges.append((u, v))

    return edges


def save_graph(path, colors, edges):
    graph = {
        "nodes": [
            {
                "id": i,
                "color": colors[i]
            }
            for i in range(len(colors))
        ],
        "links": [
            {
                "source": u,
                "target": v
            }
            for u, v in edges
        ]
    }

    with open(path, "w") as f:
        json.dump(graph, f)


def generate_unique_color():
    dataset_dir = BASE_DIR / "unique_color"
    s_dir = dataset_dir / "S_graphs"

    s_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================
    # Background graph G ~ G(1000, 0.003)
    # ========================================================

    n_g = 1000
    p_g = 0.003

    colors_g = [
        random.choice([0, 1])
        for _ in range(n_g)
    ]

    edges_g = generate_gnp_edges(n_g, p_g)

    save_graph(
        dataset_dir / "G.json",
        colors_g,
        edges_g
    )

    print(
        f"G created: "
        f"{n_g} vertices, {len(edges_g)} edges"
    )

    # ========================================================
    # Query graphs S_i ~ G(30, 0.1)
    # ========================================================

    ground_truth = {}

    for i in range(1, N_QUERIES + 1):

        n_s = 30
        p_s = 0.1

        colors_s = [
            random.choice([0, 1])
            for _ in range(n_s)
        ]

        edges_s = generate_gnp_edges(n_s, p_s)

        # Plant the unique color
        planted_vertex = random.randrange(n_s)
        colors_s[planted_vertex] = 2

        save_graph(
            s_dir / f"S_{i}.json",
            colors_s,
            edges_s
        )

        ground_truth[str(i)] = [planted_vertex]

    with open(
        dataset_dir / "ground_truth.json",
        "w"
    ) as f:
        json.dump(
            ground_truth,
            f,
            indent=2
        )

    print(f"Created {N_QUERIES} query graphs.")
    print("Unique-color dataset finished.")


if __name__ == "__main__":
    generate_unique_color()