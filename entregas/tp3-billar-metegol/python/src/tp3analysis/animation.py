"""Animacion independiente de una trayectoria ya calculada por el motor."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.patches import Circle, Rectangle

from .trajectory import Trajectory


FRESH_COLOR = "#005b91"
USED_COLOR = "#c73e36"
OBSTACLE_COLOR = "#d35c20"


def sampled_frames(trajectory: Trajectory, count: int) -> np.ndarray:
    """Selecciona cuadros reales sin interpolar estados entre eventos."""
    if count <= 0:
        raise ValueError("la cantidad de cuadros debe ser positiva")
    available = np.flatnonzero(np.array(trajectory.reasons) != "final")
    if available.size == 0:
        raise ValueError("la trayectoria no tiene cuadros de eventos")
    positions = np.linspace(0, available.size - 1, min(count, available.size))
    return available[np.unique(np.rint(positions).astype(int))]


def _base_figure(trajectory: Trajectory):
    header = trajectory.header
    fig, axis = plt.subplots(figsize=(9.6, 5.6), constrained_layout=True)
    axis.add_patch(Rectangle((0, 0), header.length, header.width, fill=False, lw=2.0))
    low = (header.width - header.goal_width) / 2
    high = (header.width + header.goal_width) / 2
    axis.plot([0, 0], [low, high], color=FRESH_COLOR, lw=5, solid_capstyle="butt")
    axis.plot(
        [header.length, header.length], [low, high],
        color=FRESH_COLOR, lw=5, solid_capstyle="butt",
    )
    for obstacle in header.obstacles:
        axis.add_patch(Circle(
            (obstacle.x, obstacle.y), obstacle.radius,
            facecolor=OBSTACLE_COLOR, edgecolor="#7f3513", lw=1.2,
        ))
    axis.set_xlim(-0.025, header.length + 0.025)
    axis.set_ylim(-0.025, header.width + 0.025)
    axis.set_aspect("equal")
    axis.set_xlabel("x [m]")
    axis.set_ylabel("y [m]")
    axis.set_title("Billar-Metegol dirigido por eventos")
    return fig, axis


def render_snapshot(trajectory: Trajectory, output: Path, frame: int) -> None:
    fig, axis = _base_figure(trajectory)
    states = trajectory.states[frame]
    colors = np.where(states == 0, FRESH_COLOR, USED_COLOR)
    size = (trajectory.header.particle_radius * 950) ** 2
    axis.scatter(
        trajectory.positions[frame, :, 0], trajectory.positions[frame, :, 1],
        s=size, c=colors, edgecolors="white", linewidths=0.3,
    )
    goals = int(states.sum())
    axis.text(
        0.02, 0.98,
        f"t = {trajectory.times[frame]:.2f} s    goles = {goals}/{trajectory.header.particle_count}",
        transform=axis.transAxes, va="top",
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"},
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def render_animation(
    trajectory: Trajectory,
    output: Path,
    fps: int = 30,
    duration: float = 15.0,
) -> None:
    if fps <= 0 or duration <= 0:
        raise ValueError("fps y duracion deben ser positivos")
    indices = sampled_frames(trajectory, round(fps * duration))
    fig, axis = _base_figure(trajectory)
    size = (trajectory.header.particle_radius * 950) ** 2
    scatter = axis.scatter([], [], s=size, edgecolors="white", linewidths=0.3)
    label = axis.text(
        0.02, 0.98, "", transform=axis.transAxes, va="top",
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"},
    )

    def update(frame_number: int):
        index = int(indices[frame_number])
        states = trajectory.states[index]
        scatter.set_offsets(trajectory.positions[index])
        scatter.set_color(np.where(states[:, None] == 0, FRESH_COLOR, USED_COLOR).ravel())
        label.set_text(
            f"t = {trajectory.times[index]:.2f} s    "
            f"goles = {int(states.sum())}/{trajectory.header.particle_count}"
        )
        return scatter, label

    animation = FuncAnimation(fig, update, frames=len(indices), interval=1000 / fps, blit=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        import imageio_ffmpeg

        matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as error:
        raise RuntimeError("falta imageio-ffmpeg para escribir MP4") from error
    animation.save(output, writer=FFMpegWriter(fps=fps, bitrate=1800))
    plt.close(fig)
