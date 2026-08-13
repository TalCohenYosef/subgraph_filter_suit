"""Plot the minimal structures used by the toy-model datasets.

Usage:
    python plot_unique_structures.py \
        --results-dir /path/to/pipeline/results \
        --output unique_structures.pdf

The results directory is optional. If omitted, the verification panel shows
the expected 1000/1000 zero-match result for each dataset.
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle


DATASETS = ["Unique color", "Unique pair", "Unique triangle"]
COLORS = ["#E45756", "#4C78A8", "#59A14F"]


def node(ax, x, y, color, label=None, size=850):
    ax.scatter([x], [y], s=size, c=[color], edgecolors="white", linewidths=2,
               zorder=3)
    if label is not None:
        ax.text(x, y, label, ha="center", va="center", color="white",
                fontsize=10, weight="bold", zorder=4)


def edge(ax, x1, y1, x2, y2, color="#555555", width=2.5):
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=width, zorder=1)


def draw_structure(ax, index):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Background graph: a small schematic sample, not the full 1000-vertex G.
    ax.text(2.4, 5.45, "Background $G$", ha="center", fontsize=11,
            weight="bold")
    for x, y in [(1, 4.5), (2.5, 4.0), (3.7, 4.6), (1.4, 2.8), (3.0, 2.5)]:
        node(ax, x, y, "#BDBDBD", size=420)
    for u, v in [((1, 4.5), (2.5, 4.0)), ((2.5, 4.0), (3.7, 4.6)),
                 ((1, 4.5), (1.4, 2.8)), ((1.4, 2.8), (3.0, 2.5)),
                 ((2.5, 4.0), (3.0, 2.5))]:
        edge(ax, *u, *v, color="#AAAAAA", width=1.8)
    if index == 0:
        ax.text(2.4, 1.05, "target color absent", ha="center", fontsize=9)
    elif index == 1:
        ax.text(2.4, 1.05, "no 2–3 edge", ha="center", fontsize=9)
    else:
        ax.text(2.4, 1.05, "no 0–0–0 triangle", ha="center", fontsize=9)

    # Query graph: the planted distinguishing structure.
    ax.text(7.5, 5.45, "$S_i$", ha="center", fontsize=11, weight="bold")
    if index == 0:
        node(ax, 7.5, 3.2, COLORS[index], "2", size=1100)
        ax.text(7.5, 1.05, "one vertex", ha="center", fontsize=9)
    elif index == 1:
        edge(ax, 6.4, 3.2, 8.6, 3.2, color="#333333", width=3)
        node(ax, 6.4, 3.2, COLORS[index], "2", size=950)
        node(ax, 8.6, 3.2, COLORS[index], "3", size=950)
        ax.text(7.5, 1.05, "two vertices + one edge", ha="center", fontsize=9)
    else:
        points = [(7.5, 4.15), (6.35, 2.35), (8.65, 2.35)]
        for a, b in [(points[0], points[1]), (points[0], points[2]),
                     (points[1], points[2])]:
            edge(ax, *a, *b, color="#333333", width=3)
        for x, y in points:
            node(ax, x, y, COLORS[index], "0", size=850)
        ax.text(7.5, 1.05, "three vertices + three edges", ha="center", fontsize=9)

    ax.text(5, 3.2, "→", ha="center", va="center", fontsize=25,
            color="#666666")


def read_verification(results_dir):
    values = [1000, 1000, 1000]
    if results_dir is None:
        return values

    for index, name in enumerate(("unique_color", "unique_pair", "unique_triangle")):
        folder = Path(results_dir) / name
        counts = []
        for path in folder.glob("S_*/smallest_match_count.txt"):
            try:
                counts.append(int(path.read_text().strip()))
            except ValueError:
                pass
        if counts:
            values[index] = sum(count == 0 for count in counts)
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path)
    parser.add_argument("--output", type=Path, default=Path("unique_structures.pdf"))
    args = parser.parse_args()

    fig = plt.figure(figsize=(13, 7), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=[2.1, 1], hspace=0.15)

    for index, title in enumerate(DATASETS):
        ax = fig.add_subplot(grid[0, index])
        ax.set_title(title, fontsize=13, pad=12)
        draw_structure(ax, index)

    ax = fig.add_subplot(grid[1, :])
    zero_matches = read_verification(args.results_dir)
    bars = ax.bar(DATASETS, zero_matches, color=COLORS, width=0.55)
    ax.set_ylim(0, 1050)
    ax.set_ylabel("Queries with minimum match count = 0")
    ax.set_title("Verification", fontsize=13, pad=10)
    ax.set_yticks([0, 250, 500, 750, 1000])
    ax.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, zero_matches):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 18,
                f"{value}/1000", ha="center", weight="bold")

    fig.suptitle("Minimal colored structures separating $S_i$ from $G$",
                 fontsize=17, weight="bold")
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    print(f"Saved figure to {args.output}")


if __name__ == "__main__":
    main()
