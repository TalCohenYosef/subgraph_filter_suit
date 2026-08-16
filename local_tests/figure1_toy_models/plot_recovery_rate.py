"""Plot planted-structure recovery versus the measured pattern-size budget."""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


DATASETS = (
    ("Unique color", "#2864ba", 1),
    ("Unique pair", "#ff6f0e", 2),
    ("Unique triangle", "#15951c", 3),
)


def read_recovery_rate(summary_path, budget):
    recovered = 0
    total = 0
    with summary_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            total += 1
            size = row.get("pattern_size", "").strip()
            if not size or int(size) != budget:
                raise ValueError(f"Pattern size is not k={budget} in {summary_path}")
            recovered += row.get("best_matches", "").strip() == "0"
    if total == 0:
        raise ValueError(f"No S rows found in {summary_path}")
    return recovered / total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-dirs", type=Path, nargs=3, required=True,
        metavar=("UNIQUE_COLOR", "UNIQUE_PAIR", "UNIQUE_TRIANGLE"),
        help="Three pipeline result directories, in the displayed order.",
    )
    parser.add_argument("--max-k", type=int, default=5)
    parser.add_argument("--output", type=Path, default=Path("recovery_rate.png"))
    args = parser.parse_args()

    if args.max_k < 1:
        parser.error("--max-k must be positive")

    fig, ax = plt.subplots(figsize=(10.5, 5.5), constrained_layout=True)
    budgets = list(range(1, args.max_k + 1))

    for result_dir, (label, color, planted_size) in zip(args.results_dirs, DATASETS):
        dataset_budgets = [1] if label == "Unique color" else budgets
        rates = []
        for budget in dataset_budgets:
            summary_path = result_dir / f"k_{budget}" / "summary.csv"
            rates.append(read_recovery_rate(summary_path, budget))
        ax.plot(dataset_budgets, rates, "o-", color=color, linewidth=2, label=label)
        ax.axvline(planted_size, color=color, linestyle=":", alpha=0.55)
        ax.text(planted_size, 1.025, rf"$k^*={planted_size}$", color=color,
                ha="center", transform=ax.get_xaxis_transform())

    ax.set_title("Planted-structure recovery", weight="bold")
    ax.set_xlabel(r"subgraph-size budget $k$ (number of vertices)")
    ax.set_ylabel(r"Recovery rate $R(k)$")
    ax.set_xticks(budgets)
    ax.set_ylim(-0.03, 1.08)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    print(f"Saved figure to {args.output}")


if __name__ == "__main__":
    main()
