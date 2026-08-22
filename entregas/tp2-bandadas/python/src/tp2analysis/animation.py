from __future__ import annotations

import math
from pathlib import Path

from .data import ParticleState, group_frames


def animate(
    states: list[ParticleState],
    output: str | Path,
    side: float,
    fps: int = 20,
) -> None:
    if side <= 0 or fps <= 0:
        raise ValueError("L y fps deben ser positivos")
    frames = group_frames(states)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter

    figure, axis = plt.subplots(figsize=(7, 7))
    axis.set_xlim(0, side)
    axis.set_ylim(0, side)
    axis.set_aspect("equal")
    axis.set_xlabel("x")
    axis.set_ylabel("y")
    first = frames[0][1]
    quiver = axis.quiver(
        [state.x for state in first],
        [state.y for state in first],
        [state.vx for state in first],
        [state.vy for state in first],
        [(state.angle + math.pi) / (2 * math.pi) for state in first],
        cmap="hsv",
        clim=(0, 1),
        angles="xy",
        scale_units="xy",
        scale=0.15,
        width=0.004,
    )
    title = axis.set_title(f"t = {frames[0][0]:g}")

    def update(frame_index: int):
        time, frame = frames[frame_index]
        quiver.set_offsets([(state.x, state.y) for state in frame])
        quiver.set_UVC(
            [state.vx for state in frame],
            [state.vy for state in frame],
            [(state.angle + math.pi) / (2 * math.pi) for state in frame],
        )
        title.set_text(f"t = {time:g}")
        return quiver, title

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
