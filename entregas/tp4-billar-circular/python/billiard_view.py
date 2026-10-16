"""Animacion independiente del sistema fisico; solo lee estados del motor."""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "python/.matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / "python/.cache"))
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
import numpy as np

from billiard_analysis import frames


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trajectory", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="GIF local del sistema")
    parser.add_argument("--snapshot", type=Path, help="PNG del ultimo cuadro")
    parser.add_argument("--fps", type=int, default=25)
    parser.add_argument("--frame-stride", type=int, default=1)
    args = parser.parse_args()
    if args.fps <= 0 or args.frame_stride <= 0 or args.output.suffix.lower() != ".gif":
        parser.error("fps y frame-stride positivos; output con extension .gif")
    metadata = args.metadata or Path(str(args.trajectory) + ".json")
    config = json.loads(metadata.read_text())
    fig, ax = plt.subplots(figsize=(6, 6), layout="constrained")
    radius = config["radius"]
    ax.add_patch(Circle((0, 0), radius, fill=False, color="black", linewidth=1.5))
    if config["obstacles"]:
        for x in [-config["obstacle_x"], config["obstacle_x"]]:
            ax.add_patch(Circle((x, 0), config["particle_radius"], color="black"))
    collection = PatchCollection([], edgecolors="none")
    ax.add_collection(collection)
    ax.set(xlim=(-radius * 1.04, radius * 1.04), ylim=(-radius * 1.04, radius * 1.04),
           xlabel="x (m)", ylabel="y (m)", aspect="equal")
    title = ax.set_title("", pad=30)
    handles = [Line2D([], [], linestyle="none", marker="o", color=color, label=label)
               for label, color in [("Frescas", "#1f77b4"), ("Usadas", "#d62728")]]
    if config["obstacles"]:
        handles.append(Line2D([], [], linestyle="none", marker="o", color="black", label="Obstáculos"))
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, 1.005),
              ncol=len(handles), frameon=False, fontsize=9)

    def selected_frames():
        for index, item in enumerate(frames(args.trajectory, config)):
            if index % args.frame_stride == 0 or item[0] == config["steps"]:
                yield item

    def update(item):
        _, time, state = item
        collection.set_paths([Circle(tuple(p), config["particle_radius"]) for p in state[:, 3:5]])
        collection.set_facecolor(np.where(state[:, 7, None] == 0,
            np.array([.12, .47, .71, 1]), np.array([.84, .15, .16, 1])))
        title.set_text(f"Billar circular · N={config['n']} · t={time:.3f} s")
        return collection, title

    movie = FuncAnimation(fig, update, frames=selected_frames, init_func=lambda: (),
                          interval=1000 / args.fps, cache_frame_data=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    movie.save(args.output, writer=PillowWriter(fps=args.fps), dpi=90)
    if args.snapshot:
        args.snapshot.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.snapshot, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
