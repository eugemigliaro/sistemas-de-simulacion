#!/usr/bin/env python3
"""Animaciones de la presentación: MP4 para la exposición y un fotograma PNG
para el PDF [GPRES, pp. 2-3]. Leen los archivos que escribe el motor."""
import numpy as np

from common import FIGURES, PARTICLE_RADIUS, RADIUS, RAW, VIDEOS, billiard, require_engine
from tp4analysis import files
from tp4analysis.animation import animate

MIDDLE = round(PARTICLE_RADIUS + 5 * (RADIUS - 2 * PARTICLE_RADIUS) / 10, 6)

# Nombre -> (corridas (N, x0), tf, intervalo de salida, cuadros por segundo, color por rapidez, cuadro del póster).
VIDEO_SPECS = {
    "densidad": ([(20, PARTICLE_RADIUS), (650, PARTICLE_RADIUS)], 30.0, 0.04, 50, False, 0.5),
    "posicion": ([(100, PARTICLE_RADIUS), (100, MIDDLE), (100, RADIUS - PARTICLE_RADIUS)], 30.0, 0.04, 50, False, 0.4),
    "rapidez": ([(100, None)], 4.0, 0.01, 40, True, 0.25),
}
POSITION_NAMES = {PARTICLE_RADIUS: "r", MIDDLE: "R/2", RADIUS - PARTICLE_RADIUS: "R − r"}


def title(n: int, x0: float | None, name: str) -> str:
    if name == "densidad":
        return f"N = {n}"
    if name == "posicion":
        return f"$x_0$ = {POSITION_NAMES[x0]}"
    return ""


def main() -> None:
    require_engine()
    VIDEOS.mkdir(parents=True, exist_ok=True)
    for name, (runs, tf, interval, fps, by_speed, poster_at) in VIDEO_SPECS.items():
        trajectories = [files.read_billiard(billiard(RAW / "anim" / f"{name}-n{n}-x{x0}.txt", n, tf, interval, 1, x0=x0))
                        for n, x0 in runs]
        frames = np.arange(len(trajectories[0].times))
        animate(trajectories, [title(n, x0, name) for n, x0 in runs], VIDEOS / f"{name}.mp4", frames, fps=fps,
                by_speed=by_speed, poster=FIGURES / f"anim-{name}.png", poster_frame=int(poster_at * (len(frames) - 1)))
        speedup = interval * fps
        print(f"video {name}: {len(frames) / fps:.0f} s, {speedup:g} veces la velocidad real")


if __name__ == "__main__":
    main()
