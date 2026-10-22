"""Animaciones independientes del motor: leen los estados guardados y escriben MP4."""
from __future__ import annotations

from pathlib import Path

import imageio_ffmpeg
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import EllipseCollection  # noqa: E402
from matplotlib.colors import Normalize, to_rgb  # noqa: E402

import numpy as np  # noqa: E402

from .files import Trajectory  # noqa: E402

FRESH = "#1f5fbf"
USED = "#d0392f"


def _panel(axis, trajectory: Trajectory, title: str, speed_norm: Normalize | None):
    h = trajectory.header
    radius, r = h["radius"], h["particle_radius"]
    axis.set_xlim(-radius * 1.03, radius * 1.03)
    axis.set_ylim(-radius * 1.03, radius * 1.03)
    axis.set_aspect("equal")
    axis.axis("off")
    axis.add_patch(plt.Circle((0, 0), radius, fill=False, color="black", linewidth=2))
    if h.get("obstacle_x") is not None:
        for x0 in (-h["obstacle_x"], h["obstacle_x"]):
            axis.add_patch(plt.Circle((x0, 0), r, color="black"))
    n = trajectory.states.shape[1]
    diameters = np.full(n, 2 * r)
    disks = EllipseCollection(diameters, diameters, np.zeros(n), units="xy", offsets=trajectory.positions[0],
                              offset_transform=axis.transData, edgecolors="none")
    if speed_norm is not None:
        disks.set_cmap("viridis")
        disks.set_norm(speed_norm)
    axis.add_collection(disks)
    axis.set_title(title, fontsize=22)
    return disks


def _paint(disks: EllipseCollection, trajectory: Trajectory, frame: int, by_speed: bool) -> None:
    disks.set_offsets(trajectory.positions[frame])
    if by_speed:
        disks.set_array(np.linalg.norm(trajectory.velocities[frame], axis=1))
    else:
        disks.set_facecolors(np.where(trajectory.used[frame][:, None], [to_rgb(USED)], [to_rgb(FRESH)]))


def animate(
    trajectories: list[Trajectory],
    titles: list[str],
    output: Path,
    frames: np.ndarray,
    fps: int = 30,
    by_speed: bool = False,
    poster: Path | None = None,
    poster_frame: int = 0,
) -> None:
    """Escribe un MP4 con un panel por trayectoria, recorriendo los cuadros
    indicados (los mismos índices en todas). Opcionalmente guarda un PNG
    representativo para el PDF."""
    panels = len(trajectories)
    extra = 2.0 if by_speed else 0.0
    width_inches = 5.4 * panels + extra
    figure, axes = plt.subplots(1, panels, figsize=(width_inches, 6.0), dpi=100, squeeze=False)
    norm = Normalize(0.0, 2.5) if by_speed else None
    disks = [_panel(axis, t, title, norm) for axis, t, title in zip(axes[0], trajectories, titles)]
    panel_right = 1.0 - extra / width_inches
    figure.subplots_adjust(left=0.02, right=panel_right - 0.01, top=0.88, bottom=0.1, wspace=0.05)
    if by_speed:
        bar_axis = figure.add_axes((panel_right + 0.02, 0.15, 0.04, 0.7))
        bar = figure.colorbar(disks[-1], cax=bar_axis)
        bar.set_label("Rapidez (m/s)", fontsize=20)
        bar.ax.tick_params(labelsize=16)
        bar.ax.yaxis.set_major_formatter(lambda value, _: f"{value:g}".replace(".", ","))
    clock = figure.text((panel_right - 0.01) / 2 + 0.01, 0.03, "", ha="center", fontsize=20)
    figure.canvas.draw()
    width, height = figure.canvas.get_width_height()
    writer = imageio_ffmpeg.write_frames(str(output), (width, height), fps=fps, quality=6,
                                         macro_block_size=1, pix_fmt_out="yuv420p")
    writer.send(None)
    try:
        for index in frames:
            for panel, trajectory in zip(disks, trajectories):
                _paint(panel, trajectory, index, by_speed)
            clock.set_text(f"t = {trajectories[0].times[index]:.1f} s".replace(".", ","))
            figure.canvas.draw()
            image = np.asarray(figure.canvas.buffer_rgba())[:, :, :3]
            writer.send(np.ascontiguousarray(image))
            if poster is not None and index == frames[poster_frame]:
                figure.savefig(poster, dpi=100)
    finally:
        writer.close()
        plt.close(figure)
