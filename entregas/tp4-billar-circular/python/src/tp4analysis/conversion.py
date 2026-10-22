"""Fracción de partículas usadas y tiempos característicos de cada realización."""
from __future__ import annotations

import numpy as np

from .files import Trajectory


def used_fraction(trajectory: Trajectory) -> np.ndarray:
    """Fu(t) = Nu(t) / N en cada cuadro guardado [TP04, p. 3]."""
    return trajectory.used.mean(axis=1)


def crossing_time(times: np.ndarray, fraction: np.ndarray, level: float) -> float | None:
    """Primer tiempo guardado con Fu >= level; None si la corrida no llega."""
    reached = np.nonzero(fraction >= level - 1e-12)[0]
    return float(times[reached[0]]) if len(reached) else None


def summarize_run(trajectory: Trajectory) -> dict:
    fraction = used_fraction(trajectory)
    return {
        "t90": crossing_time(trajectory.times, fraction, 0.9),
        "t100": crossing_time(trajectory.times, fraction, 1.0),
        "fu_final": float(fraction[-1]),
        "times": trajectory.times,
        "fu": fraction,
    }
