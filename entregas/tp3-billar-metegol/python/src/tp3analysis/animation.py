"""Animacion independiente de una trayectoria ya calculada por el motor."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.patches import Circle, Rectangle

from .goals import goal_curve, time_to_fraction
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


def event_frames_at(trajectory: Trajectory, times: np.ndarray) -> np.ndarray:
    """Último cuadro de evento anterior o igual a cada instante pedido.

    Permite reproducir en tiempo real sin interpolar estados: cada instante
    muestra el último estado que el motor calculó.
    """
    available = np.flatnonzero(np.array(trajectory.reasons) != "final")
    if available.size == 0:
        raise ValueError("la trayectoria no tiene cuadros de eventos")
    position = np.searchsorted(trajectory.times[available], times, side="right") - 1
    return available[np.clip(position, 0, available.size - 1)]


def _draw_table(axis, trajectory: Trajectory) -> None:
    header = trajectory.header
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


def _base_figure(trajectory: Trajectory):
    fig, axis = plt.subplots(figsize=(9.6, 5.6), constrained_layout=True)
    _draw_table(axis, trajectory)
    axis.set_title("Billar-Metegol dirigido por eventos")
    return fig, axis


class _GoalPanel:
    """Mesa arriba y Fu(t) abajo, dibujada hasta el instante mostrado."""

    def __init__(self, trajectory: Trajectory, end_time: float) -> None:
        self.trajectory = trajectory
        self.curve = goal_curve(trajectory)
        self.t90 = time_to_fraction(trajectory).t90
        self.fig = plt.figure(figsize=(9.6, 7.6), constrained_layout=True)
        grid = self.fig.add_gridspec(2, 1, height_ratios=(2.2, 1.0))
        self.table = self.fig.add_subplot(grid[0])
        _draw_table(self.table, trajectory)
        size = (trajectory.header.particle_radius * 950) ** 2
        self.scatter = self.table.scatter([], [], s=size, edgecolors="white", linewidths=0.3)
        self.label = self.table.text(
            0.02, 0.98, "", transform=self.table.transAxes, va="top",
            bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"},
        )
        self.fu = self.fig.add_subplot(grid[1])
        self.fu.set_xlim(0, end_time)
        self.fu.set_ylim(0, 1.03)
        self.fu.set_xlabel("t [s]")
        self.fu.set_ylabel(r"$F_u$")
        self.fu.axhline(0.9, color="0.55", ls=":", lw=1.2)
        self.fu.grid(True, alpha=0.25)
        (self.line,) = self.fu.plot([], [], color=USED_COLOR, lw=2.0, drawstyle="steps-post")
        self.marker = self.fu.axvline(self.t90 or 0.0, color=FRESH_COLOR, ls="--", lw=1.5,
                                      visible=False)
        self.t90_text = self.fu.text(
            0, 0.45, "", color=FRESH_COLOR, ha="left", va="center",
            bbox={"facecolor": "white", "alpha": 0.9, "edgecolor": "none"},
        )

    def show(self, time: float) -> None:
        index = int(event_frames_at(self.trajectory, np.array([time]))[0])
        states = self.trajectory.states[index]
        self.scatter.set_offsets(self.trajectory.positions[index])
        self.scatter.set_color(np.where(states[:, None] == 0, FRESH_COLOR, USED_COLOR).ravel())
        count = self.trajectory.header.particle_count
        self.label.set_text(f"t = {time:5.2f} s    goles = {int(states.sum())}/{count}")
        steps = np.searchsorted(self.curve.times, time, side="right")
        xs = np.append(self.curve.times[:steps], time)
        ys = np.append(self.curve.used_fraction[:steps], self.curve.used_fraction[steps - 1])
        self.line.set_data(xs, ys)
        reached = self.t90 is not None and time >= self.t90
        self.marker.set_visible(reached)
        if reached:
            self.t90_text.set_position((self.t90 + 0.012 * self.fu.get_xlim()[1], 0.45))
            self.t90_text.set_text(rf"$t_{{90}} = {self.t90:.1f}$ s")
        else:
            self.t90_text.set_text("")


def render_goal_snapshot(trajectory: Trajectory, output: Path, time: float,
                         end_time: float) -> None:
    """Fotograma de la animación con Fu(t): el que va en el PDF."""
    panel = _GoalPanel(trajectory, end_time)
    panel.show(time)
    output.parent.mkdir(parents=True, exist_ok=True)
    panel.fig.savefig(output, dpi=180)
    plt.close(panel.fig)


def render_goal_animation(trajectory: Trajectory, output: Path, end_time: float,
                          fps: int = 30) -> None:
    """Animación en tiempo real (1 s de video = 1 s simulado) con Fu(t) debajo."""
    if fps <= 0 or end_time <= 0:
        raise ValueError("fps y end_time deben ser positivos")
    if end_time > trajectory.final_time:
        raise ValueError("end_time supera el tiempo simulado")
    panel = _GoalPanel(trajectory, end_time)
    times = np.arange(0.0, end_time + 1e-9, 1.0 / fps)

    def update(frame_number: int):
        panel.show(float(times[frame_number]))
        return ()

    animation = FuncAnimation(panel.fig, update, frames=times.size, interval=1000 / fps,
                              blit=False)
    _save_mp4(animation, output, fps)
    plt.close(panel.fig)


def _save_mp4(animation: FuncAnimation, output: Path, fps: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        import imageio_ffmpeg

        matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as error:
        raise RuntimeError("falta imageio-ffmpeg para escribir MP4") from error
    animation.save(output, writer=FFMpegWriter(fps=fps, bitrate=2400))


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
    _save_mp4(animation, output, fps)
    plt.close(fig)
