"""Trayectorias sintéticas en el formato del motor, para tests."""

from __future__ import annotations

from typing import Sequence

Row = tuple[float, float, float, float, int]
Frame = tuple[float, int, str, Sequence[Row]]


def trajectory_text(
    frames: Sequence[Frame],
    particle_count: int,
    seed: int = 1,
    max_time: float | None = None,
    obstacles: Sequence[tuple[float, float, float]] = (),
) -> str:
    lines = [
        "# tp3-trajectory 1",
        "# length 1.2",
        "# width 0.68",
        "# goal_width 0.2",
        f"# particle_count {particle_count}",
        "# particle_radius 0.0175",
        "# particle_mass 0.025",
        "# initial_speed 1",
        f"# seed {seed}",
        "# save_every 1",
    ]
    if max_time is not None:
        lines += [f"# max_time {max_time}", "# max_events 0"]
    lines.append(f"# obstacle_count {len(obstacles)}")
    lines += [f"# obstacle {x} {y} {radius}" for x, y, radius in obstacles]
    lines.append("# frame_columns x y vx vy state")
    for index, (time, events, reason, rows) in enumerate(frames):
        lines.append(f"frame {index} {time} {events} {reason}")
        lines += [f"{x} {y} {vx} {vy} {state}" for x, y, vx, vy, state in rows]
    return "\n".join(lines) + "\n"


def still_rows(states: Sequence[int]) -> list[Row]:
    """Partículas quietas en posiciones fijas, con los estados dados."""
    return [(0.1 + 0.05 * i, 0.3, 0.0, 0.0, state) for i, state in enumerate(states)]
