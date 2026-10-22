"""Energía total del billar calculada desde los estados guardados."""
from __future__ import annotations

import numpy as np

from .files import Trajectory


def _spring(overlap: np.ndarray, stiffness: float) -> np.ndarray:
    overlap = np.maximum(overlap, 0.0)
    return 0.5 * stiffness * overlap**2


def total_energy(trajectory: Trajectory, chunk: int = 64) -> np.ndarray:
    """Cinética más potencial elástica k xi^2 / 2 de cada contacto [T04, p. 42].

    Cada par se cuenta una vez; la pared y los obstáculos suman su propio
    resorte. Devuelve un valor por cuadro.
    """
    h = trajectory.header
    m, k, radius, r = h["particle_mass"], h["stiffness"], h["radius"], h["particle_radius"]
    positions, velocities = trajectory.positions, trajectory.velocities
    i, j = np.triu_indices(positions.shape[1], 1)
    energy = 0.5 * m * np.sum(velocities**2, axis=(1, 2))
    for start in range(0, len(positions), chunk):
        p = positions[start:start + chunk]
        distances = np.linalg.norm(p[:, i] - p[:, j], axis=2)
        energy[start:start + chunk] += _spring(2 * r - distances, k).sum(axis=1)
    energy += _spring(np.linalg.norm(positions, axis=2) + r - radius, k).sum(axis=1)
    if h.get("obstacle_x") is not None:
        for x0 in (-h["obstacle_x"], h["obstacle_x"]):
            distances = np.linalg.norm(positions - np.array([x0, 0.0]), axis=2)
            energy += _spring(2 * r - distances, k).sum(axis=1)
    return energy


def relative_deviation(energy: np.ndarray) -> np.ndarray:
    """|E(t) - E(0)| / E(0)."""
    return np.abs(energy / energy[0] - 1.0)
