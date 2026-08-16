"""Render the three toy-dataset figures and combine them into one PNG."""

import os
import subprocess
import sys
from pathlib import Path

from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
PLOTS = (
    ("plot_images.py", "unique_color_dataset.png"),
    ("test.py", "unique_pair_dataset.png"),
    ("plot_test_tringle.py", "unique_triangle_dataset.png"),
)


def render_plots():
    environment = os.environ.copy()
    environment["MPLBACKEND"] = "Agg"
    for script_name, output_name in PLOTS:
        print(f"Rendering {output_name} ...")
        subprocess.run(
            [sys.executable, str(SCRIPT_DIR / script_name)],
            cwd=SCRIPT_DIR,
            env=environment,
            check=True,
        )


def combine_plots(output_path):
    images = [Image.open(SCRIPT_DIR / name).convert("RGB") for _, name in PLOTS]
    target_width = max(image.width for image in images)
    resized = []

    for image in images:
        if image.width != target_width:
            target_height = round(image.height * target_width / image.width)
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        resized.append(image)

    gap = 50
    canvas_height = sum(image.height for image in resized) + gap * (len(resized) - 1)
    canvas = Image.new("RGB", (target_width, canvas_height), "white")

    y = 0
    for image in resized:
        canvas.paste(image, (0, y))
        y += image.height + gap

    canvas.save(output_path, dpi=(300, 300))
    print(f"Saved combined figure to {output_path}")


def main():
    output_path = SCRIPT_DIR / "combined_toy_datasets.png"
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"}):
        print(f"Usage: {Path(sys.argv[0]).name} [OUTPUT.png]")
        return
    if len(sys.argv) == 2:
        output_path = Path(sys.argv[1]).expanduser().resolve()

    render_plots()
    combine_plots(output_path)


if __name__ == "__main__":
    main()
