import json
import random
from pathlib import Path


SEED = 42
N_QUERIES = 1000

random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "unique_pair_graphs"
S_DIR = DATASET_DIR / "S_graphs"


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


def generate_uniform_colors(n):
    return [
        random.choice([0, 1])
        for _ in range(n)
    ]


def generate_same_color_edges(colors, p):
    """
    Generate edges independently with probability p,
    but ONLY between vertices having the same color.
    """

    edges = []
    n = len(colors)

    for u in range(n):
        for v in range(u + 1, n):

            if colors[u] != colors[v]:
                continue

            if random.random() < p:
                edges.append((u, v))

    return edges


def generate_background():
    """
    G:
        n = 1000
        colors = {0,1} uniformly
        same-color edges only
        p = 0.003
    """

    n_g = 1000
    p_g = 0.003

    colors = generate_uniform_colors(n_g)
    edges = generate_same_color_edges(colors, p_g)

    save_graph(
        DATASET_DIR / "G.json",
        colors,
        edges
    )

    n0 = colors.count(0)
    n1 = colors.count(1)

    print("Background G created")
    print(f"Vertices: {n_g}")
    print(f"Color 0:  {n0}")
    print(f"Color 1:  {n1}")
    print(f"Edges:    {len(edges)}")


def generate_queries():
    """
    Each S_i:
        n = 30
        colors = {0,1} uniformly
        same-color edges only with p = 0.1

    Then plant exactly one 0-1 edge.
    """

    n_s = 30
    p_s = 0.1

    ground_truth = {}

    for i in range(1, N_QUERIES + 1):

        # Very unlikely, but make sure both colors exist.
        while True:
            colors = generate_uniform_colors(n_s)

            color_0_vertices = [
                v for v, c in enumerate(colors)
                if c == 0
            ]

            color_1_vertices = [
                v for v, c in enumerate(colors)
                if c == 1
            ]

            if color_0_vertices and color_1_vertices:
                break

        # Initially ONLY same-color edges.
        edges = generate_same_color_edges(
            colors,
            p_s
        )

        # ----------------------------------------------------
        # Plant the unique cross-color pair
        # ----------------------------------------------------

        u = random.choice(color_0_vertices)
        v = random.choice(color_1_vertices)

        # This edge cannot already exist because initially
        # cross-color edges are forbidden.
        edges.append((u, v))

        save_graph(
            S_DIR / f"S_{i}.json",
            colors,
            edges
        )

        # Save the planted pair U_i*
        ground_truth[str(i)] = [u, v]

    with open(
        DATASET_DIR / "ground_truth.json",
        "w"
    ) as f:
        json.dump(
            ground_truth,
            f,
            indent=2
        )

    print()
    print(f"Created {N_QUERIES} query graphs.")
    print("Unique-pair dataset finished.")


if __name__ == "__main__":

    DATASET_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    S_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    generate_background()
    generate_queries()