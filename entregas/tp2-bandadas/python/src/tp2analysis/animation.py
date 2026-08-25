from __future__ import annotations

import math
from pathlib import Path

from .data import (
    Observation,
    ParticleState,
    group_frames,
    observation_run_key,
    trajectory_run_key,
)


_MODEL = {"vicsek": "Vicsek", "voter": "Votante"}


def _normalized_angle(angle: float) -> float:
    return (angle + math.pi) / (2 * math.pi)


def _draw_angle_wheel(axis, matplotlib) -> None:
    from matplotlib.collections import PatchCollection
    from matplotlib.patches import Wedge

    segment_count = 180
    width_degrees = 360.0 / segment_count
    wedges = []
    colors = []
    color_map = matplotlib.colormaps["hsv"]
    for index in range(segment_count):
        start_degrees = index * width_degrees
        middle_angle = math.radians(start_degrees + width_degrees / 2)
        physical_angle = (
            (middle_angle + math.pi) % (2 * math.pi)
        ) - math.pi
        wedges.append(
            Wedge(
                (0.0, 0.0),
                1.0,
                start_degrees,
                start_degrees + width_degrees,
                width=0.28,
            )
        )
        colors.append(color_map(_normalized_angle(physical_angle)))
    wheel = PatchCollection(
        wedges,
        facecolors=colors,
        edgecolors="none",
        antialiased=False,
    )
    axis.add_collection(wheel)
    for angle in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
        axis.plot(
            [0.68 * math.cos(angle), 1.03 * math.cos(angle)],
            [0.68 * math.sin(angle), 1.03 * math.sin(angle)],
            color="black",
            linewidth=0.8,
        )
    axis.text(1.12, 0.0, "0°  →", ha="left", va="center")
    axis.text(0.0, 1.12, "90°  ↑", ha="center", va="bottom")
    axis.text(-1.12, 0.0, "←  ±180°", ha="right", va="center")
    axis.text(0.0, -1.12, "↓  −90°", ha="center", va="top")
    axis.text(0.0, 0.0, "θ", ha="center", va="center", fontsize=12)
    axis.set_xlim(-1.75, 1.75)
    axis.set_ylim(-1.35, 1.35)
    axis.set_aspect("equal")
    axis.set_title("Color según la dirección de la velocidad", fontsize=10, pad=2)
    axis.axis("off")


def _synchronized_observations(
    frames: list[tuple[float, list[ParticleState]]],
    observations: list[Observation],
) -> list[Observation]:
    if not observations:
        raise ValueError("la animación requiere observaciones de va y S")
    expected_observation_key = observation_run_key(observations[0])
    if any(observation_run_key(row) != expected_observation_key for row in observations):
        raise ValueError("las observaciones mezclan corridas diferentes")
    trajectory_key = trajectory_run_key(frames[0][1][0])
    if trajectory_key != expected_observation_key:
        raise ValueError("la trayectoria y las observaciones no pertenecen a la misma corrida")

    by_time: dict[float, Observation] = {}
    for row in observations:
        if row.time in by_time:
            raise ValueError(f"observación duplicada en t={row.time:g}")
        by_time[row.time] = row
    result: list[Observation] = []
    for time, _frame in frames:
        if time not in by_time:
            raise ValueError(f"falta observación para el cuadro t={time:g}")
        result.append(by_time[time])
    return result


def animate(
    states: list[ParticleState],
    observations: list[Observation],
    output: str | Path,
    side: float | None = None,
    fps: float = 5.0,
) -> None:
    if not math.isfinite(fps) or fps <= 0:
        raise ValueError("fps debe ser positivo")
    frames = group_frames(states)
    synchronized = _synchronized_observations(frames, observations)
    actual_side = frames[0][1][0].side if side is None else side
    if not math.isfinite(actual_side) or actual_side <= 0:
        raise ValueError("L debe ser positivo")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter

    figure = plt.figure(figsize=(11, 7.5), layout="constrained")
    grid = figure.add_gridspec(2, 2, width_ratios=(1.25, 1.0))
    left_grid = grid[:, 0].subgridspec(
        2,
        1,
        height_ratios=(4.8, 1.3),
    )
    particle_axis = figure.add_subplot(left_grid[0, 0])
    angle_axis = figure.add_subplot(left_grid[1, 0])
    polarization_axis = figure.add_subplot(grid[0, 1])
    cluster_axis = figure.add_subplot(grid[1, 1], sharex=polarization_axis)

    particle_axis.set_xlim(0, actual_side)
    particle_axis.set_ylim(0, actual_side)
    particle_axis.set_aspect("equal")
    particle_axis.set_xlabel(r"$x$")
    particle_axis.set_ylabel(r"$y$")
    first = frames[0][1]
    quiver = particle_axis.quiver(
        [state.x for state in first],
        [state.y for state in first],
        [state.vx for state in first],
        [state.vy for state in first],
        [_normalized_angle(state.angle) for state in first],
        cmap="hsv",
        clim=(0, 1),
        angles="xy",
        scale_units="xy",
        scale=0.15,
        width=0.004,
    )
    _draw_angle_wheel(angle_axis, matplotlib)

    times = [time for time, _frame in frames]
    minimum_time = min(times)
    maximum_time = max(times)
    if minimum_time == maximum_time:
        maximum_time = minimum_time + 1.0
    for axis, label in (
        (polarization_axis, r"Polarización $v_a$"),
        (cluster_axis, r"Componente gigante $S$"),
    ):
        axis.set_xlim(minimum_time, maximum_time)
        axis.set_ylim(-0.03, 1.03)
        axis.set_ylabel(label)
        axis.grid(alpha=0.25)
    cluster_axis.set_xlabel(r"Tiempo simulado $t$")

    polarization_line, = polarization_axis.plot([], [], color="tab:blue")
    cluster_line, = cluster_axis.plot([], [], color="tab:orange")
    polarization_marker, = polarization_axis.plot([], [], "o", color="tab:blue")
    cluster_marker, = cluster_axis.plot([], [], "o", color="tab:orange")
    polarization_cursor = polarization_axis.axvline(
        minimum_time, color="black", linestyle="--", alpha=0.5
    )
    cluster_cursor = cluster_axis.axvline(
        minimum_time, color="black", linestyle="--", alpha=0.5
    )
    first_observation = synchronized[0]
    title = particle_axis.set_title(
        f"{_MODEL[first_observation.model]}  |  "
        rf"$t={first_observation.time:g}$  |  "
        rf"$v_a={first_observation.polarization:.3f}$  |  "
        rf"$S={first_observation.largest_cluster_fraction:.3f}$"
    )

    def update(frame_index: int):
        time, frame = frames[frame_index]
        observation = synchronized[frame_index]
        quiver.set_offsets([(state.x, state.y) for state in frame])
        quiver.set_UVC(
            [state.vx for state in frame],
            [state.vy for state in frame],
            [_normalized_angle(state.angle) for state in frame],
        )
        visible_times = times[: frame_index + 1]
        visible_observations = synchronized[: frame_index + 1]
        polarization_values = [row.polarization for row in visible_observations]
        cluster_values = [
            row.largest_cluster_fraction for row in visible_observations
        ]
        polarization_line.set_data(visible_times, polarization_values)
        cluster_line.set_data(visible_times, cluster_values)
        polarization_marker.set_data([time], [observation.polarization])
        cluster_marker.set_data([time], [observation.largest_cluster_fraction])
        polarization_cursor.set_xdata([time, time])
        cluster_cursor.set_xdata([time, time])
        title.set_text(
            f"{_MODEL[observation.model]}  |  "
            rf"$t={time:g}$  |  "
            rf"$v_a={observation.polarization:.3f}$  |  "
            rf"$S={observation.largest_cluster_fraction:.3f}$"
        )
        return (
            quiver,
            title,
            polarization_line,
            cluster_line,
            polarization_marker,
            cluster_marker,
            polarization_cursor,
            cluster_cursor,
        )

    animation = FuncAnimation(
        figure,
        update,
        frames=len(frames),
        interval=1000 / fps,
        blit=False,
    )
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    animation.save(destination, writer=PillowWriter(fps=fps))
    plt.close(figure)
