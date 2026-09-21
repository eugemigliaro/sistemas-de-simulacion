"""Ng(t), Fu(t) y t90 a partir del color de las partículas.

Ng(t) es el número acumulado de goles, Fu(t) = Ng(t)/N y t90 el tiempo en que
Fu alcanza 0.9 [TP03, p. 3]. Como el color es estado y cambia una sola vez por
partícula, Ng es simplemente la cantidad de partículas usadas en cada cuadro.

El motor escribe un cuadro "color" en cada evento que cambia un color, así que
los escalones de Ng caen exactamente en los instantes de gol y t90 sale exacto,
sin interpolar entre cuadros.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .trajectory import Trajectory


@dataclass(frozen=True)
class GoalCurve:
    """Ng(t) como función escalón: vale goals[i] desde times[i]."""

    times: np.ndarray
    goals: np.ndarray
    particle_count: int
    end_time: float

    @property
    def used_fraction(self) -> np.ndarray:
        return self.goals / self.particle_count


@dataclass(frozen=True)
class T90Result:
    seed: int
    particle_count: int
    fraction: float
    threshold_goals: int
    reached: bool
    t90: float | None
    final_time: float
    goals_at_end: int
    # "max_time", "max_events" o "unknown" (cabecera sin max_time).
    ended_by: str
    source: str = ""


def goal_counts(trajectory: Trajectory) -> np.ndarray:
    return trajectory.states.sum(axis=1).astype(np.int64)


def goal_curve(trajectory: Trajectory) -> GoalCurve:
    counts = goal_counts(trajectory)
    steps = np.diff(counts)
    changed = np.flatnonzero(steps) + 1

    # Cada gol es un evento contra una pared, que involucra una sola
    # partícula, y el motor lo guarda en un cuadro "color". Si no, t90 no
    # sería exacto y no hay que calcularlo en silencio.
    for index in changed:
        if steps[index - 1] != 1 or trajectory.reasons[index] != "color":
            raise ValueError(
                f"cuadro {index}: Ng cambia sin su cuadro de color; "
                "t90 no puede reconstruirse con exactitud"
            )

    indices = np.concatenate(([0], changed))
    return GoalCurve(
        times=trajectory.times[indices],
        goals=counts[indices],
        particle_count=trajectory.header.particle_count,
        end_time=trajectory.final_time,
    )


def threshold_goals(particle_count: int, fraction: float) -> int:
    """Menor Ng con Ng/N >= fraction, sin depender del redondeo de 0.9·N."""
    if not 0 < fraction <= 1:
        raise ValueError("fraction debe estar en (0, 1]")
    return max(1, math.ceil(fraction * particle_count - 1e-9))


def time_to_fraction(trajectory: Trajectory, fraction: float = 0.9) -> T90Result:
    curve = goal_curve(trajectory)
    count = curve.particle_count
    threshold = threshold_goals(count, fraction)
    hits = np.flatnonzero(curve.goals >= threshold)
    reached = hits.size > 0

    # Una corrida que no llegó al umbral solo puede reportarse si terminó de
    # verdad. Un archivo truncado no dice nada sobre t90.
    if not reached and not trajectory.complete:
        raise ValueError(
            "la trayectoria no tiene cuadro final y no alcanzó el umbral: "
            "no se puede distinguir de un archivo truncado"
        )

    reached_max_time = trajectory.reached_max_time
    if reached_max_time is None:
        ended_by = "unknown"
    else:
        ended_by = "max_time" if reached_max_time else "max_events"

    return T90Result(
        seed=trajectory.header.seed,
        particle_count=count,
        fraction=fraction,
        threshold_goals=threshold,
        reached=reached,
        t90=float(curve.times[hits[0]]) if reached else None,
        final_time=trajectory.final_time,
        goals_at_end=int(curve.goals[-1]),
        ended_by=ended_by,
        source=str(trajectory.source or ""),
    )
