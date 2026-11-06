"""Animaciones independientes del motor: leen los cuadros guardados y escriben MP4 [TP05, p. 1]."""
from __future__ import annotations

from pathlib import Path

import imageio_ffmpeg
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import EllipseCollection  # noqa: E402
from matplotlib.colors import Normalize, to_rgb  # noqa: E402

import numpy as np  # noqa: E402

from .io import iter_frames, read_run  # noqa: E402

EVENT = "#2a78d6"    # EDMD
STEP = "#eb6834"     # TSDMD
INK = "#0b0b0b"
WALL = "#3a3936"
FAR = np.array([-1e3, -1e3])


def _walls(axis, side: float, door: float) -> None:
    left, right = 0.5 * (side - door), 0.5 * (side + door)
    for xs, ys in (([0, left], [0, 0]), ([right, side], [0, 0]), ([0, 0], [0, side]), ([side, side], [0, side]),
                   ([0, side], [side, side])):
        axis.plot(xs, ys, color=WALL, linewidth=2.5, solid_capstyle="butt")


def _disks(axis, radius: np.ndarray) -> EllipseCollection:
    d = 2 * radius
    disks = EllipseCollection(d, d, np.zeros(len(d)), units="xy", offsets=np.tile(FAR, (len(d), 1)),
                              offset_transform=axis.transData, edgecolors="none")
    axis.add_collection(disks)
    return disks


def _comma(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


def animate(
    source: str | Path,
    output: Path,
    every: int = 1,
    fps: int = 30,
    color: str = "mode",          # "mode": EDMD/TSDMD; "speed": rapidez
    zoom: tuple[float, float, float, float] | None = (-2.5, 2.5, -1.1, 3.0),  # respecto del centro de la puerta
    until: float | None = None,
    poster: Path | None = None,
    poster_time: float | None = None,
    caption: str = "",
) -> None:
    """Sala completa y, opcionalmente, un panel ampliado de la puerta. Escribe un MP4 y
    un PNG del instante `poster_time` (fotograma para el PDF [GPRES, pp. 2-3])."""
    run = read_run(source)
    side, door = float(run.params["side"]), float(run.params["door"])
    panels = 2 if zoom else 1
    figure, axes = plt.subplots(1, panels, figsize=(6.4 * panels, 6.9), dpi=100, squeeze=False,
                                gridspec_kw={"width_ratios": [1, 1] if zoom else [1]})
    full = axes[0][0]
    full.set_xlim(-0.5, side + 0.5)
    full.set_ylim(-1.5, side + 0.5)
    collections = [(full, _disks(full, run.radius))]
    if zoom:
        x0, x1, y0, y1 = zoom
        center = 0.5 * side
        detail = axes[0][1]
        detail.set_xlim(center + x0, center + x1)
        detail.set_ylim(y0, y1)
        collections.append((detail, _disks(detail, run.radius)))
        full.add_patch(plt.Rectangle((center + x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=INK, linewidth=1.2,
                                     linestyle="--"))
    for axis, _ in collections:
        _walls(axis, side, door)
        axis.set_aspect("equal")
        axis.axis("off")
    norm = Normalize(0.0, 1.6)
    if color == "speed":
        for _, disks in collections:
            disks.set_cmap("viridis")
            disks.set_norm(norm)
        bar = figure.colorbar(collections[-1][1], cax=figure.add_axes((0.915, 0.18, 0.015, 0.62)))
        bar.set_label("Rapidez (m/s)", fontsize=17)
        bar.ax.tick_params(labelsize=14)
        bar.ax.yaxis.set_major_formatter(lambda value, _: f"{value:g}".replace(".", ","))
    elif color == "mode" and run.scheme == "hybrid":
        for label, c in (("EDMD", EVENT), ("TSDMD", STEP)):
            full.scatter([], [], s=90, color=c, label=label)
        full.legend(loc="upper center", bbox_to_anchor=(0.5, 1.07), ncol=2, frameon=False, fontsize=16,
                    handletextpad=0.3)
    clock = figure.text(0.5, 0.03, "", ha="center", fontsize=18, color=INK)
    if caption:
        figure.text(0.5, 0.965, caption, ha="center", fontsize=17, color=INK)
    figure.subplots_adjust(left=0.01, right=0.89 if color == "speed" else 0.99, top=0.92, bottom=0.08, wspace=0.06)
    figure.canvas.draw()
    width, height = figure.canvas.get_width_height()
    writer = imageio_ffmpeg.write_frames(str(output), (width, height), fps=fps, quality=6, macro_block_size=1,
                                         pix_fmt_out="yuv420p")
    writer.send(None)
    n = run.agents
    default = to_rgb(EVENT if run.scheme == "edmd" else STEP)
    saved = False
    try:
        for frame in iter_frames(source, every=every):
            if until is not None and frame.time > until:
                break
            offsets = np.tile(FAR, (n, 1))
            offsets[frame.ids] = frame.position
            for _, disks in collections:
                disks.set_offsets(offsets)
                if color == "speed":
                    speed = np.zeros(n)
                    speed[frame.ids] = np.linalg.norm(frame.velocity, axis=1)
                    disks.set_array(speed)
                else:
                    colors = np.tile(default, (n, 1))
                    if run.scheme == "hybrid":
                        mode = np.zeros(n, dtype=int)
                        mode[frame.ids] = frame.mode
                        colors = np.where(mode[:, None] == 1, [to_rgb(EVENT)], [to_rgb(STEP)])
                    disks.set_facecolors(colors)
            clock.set_text(f"t = {_comma(frame.time)} s      adentro: {len(frame.ids)}")
            figure.canvas.draw()
            writer.send(np.ascontiguousarray(np.asarray(figure.canvas.buffer_rgba())[:, :, :3]))
            if poster is not None and not saved and poster_time is not None and frame.time >= poster_time:
                figure.savefig(poster, dpi=110)
                saved = True
    finally:
        writer.close()
        plt.close(figure)
