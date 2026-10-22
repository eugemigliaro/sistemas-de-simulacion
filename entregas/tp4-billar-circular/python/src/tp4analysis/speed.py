"""Distribución del módulo de la velocidad y ajuste de Maxwell-Boltzmann 2D."""
from __future__ import annotations

import numpy as np

from .files import Trajectory


def speeds(trajectory: Trajectory, frames) -> np.ndarray:
    """Módulos |v| de todas las partículas en los cuadros elegidos."""
    return np.linalg.norm(trajectory.velocities[frames], axis=-1).ravel()


def probability_density(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """Histograma normalizado: fracción de muestras en el bin dividida por su ancho."""
    if values.max() >= edges[-1] or values.min() < edges[0]:
        raise ValueError("hay rapideces fuera de los bins")
    counts, _ = np.histogram(values, bins=edges)
    return counts / (values.size * np.diff(edges))


def maxwell_boltzmann(v, mass: float, thermal_energy: float) -> np.ndarray:
    """f(v) = (m v / kBT) exp(-m v^2 / 2 kBT) [TP04, p. 4]."""
    v = np.asarray(v)
    return mass * v / thermal_energy * np.exp(-mass * v**2 / (2 * thermal_energy))


def fit_error(centers: np.ndarray, density: np.ndarray, mass: float, thermal_energies: np.ndarray) -> np.ndarray:
    """E(kBT) = sum_i [f_i - f(v_i, kBT)]^2 sobre los centros de los bins [T00, p. 79]."""
    model = maxwell_boltzmann(centers[None, :], mass, thermal_energies[:, None])
    return np.sum((density[None, :] - model) ** 2, axis=1)


def fit_thermal_energy(centers, density, mass: float, low: float, high: float, points: int = 2001):
    """Barre kBT en una grilla y elige el que minimiza E [T00, p. 80].

    Después refina con una grilla más fina alrededor del mínimo. Devuelve el
    kBT óptimo, la grilla gruesa y E sobre ella.
    """
    grid = np.linspace(low, high, points)
    errors = fit_error(centers, density, mass, grid)
    best = int(np.argmin(errors))
    if best in (0, points - 1):
        raise ValueError("el mínimo de E está en el borde de la grilla")
    fine = np.linspace(grid[best - 1], grid[best + 1], points)
    optimum = float(fine[np.argmin(fit_error(centers, density, mass, fine))])
    return optimum, grid, errors
