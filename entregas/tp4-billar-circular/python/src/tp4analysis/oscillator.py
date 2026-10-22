"""Solución analítica del oscilador amortiguado y error cuadrático medio."""
from __future__ import annotations

import numpy as np


def exact_position(times, mass: float, stiffness: float, damping: float, amplitude: float) -> np.ndarray:
    """r(t) = A exp(-gamma t / 2m) cos(sqrt(k/m - gamma^2/4m^2) t) [T04, p. 37]."""
    beta = damping / (2 * mass)
    omega = np.sqrt(stiffness / mass - beta**2)
    return amplitude * np.exp(-beta * np.asarray(times)) * np.cos(omega * np.asarray(times))


def mean_squared_error(header: dict, times: np.ndarray, positions: np.ndarray) -> float:
    """ECM = (1/M) sum_{n=1}^{M} [r_n - r(t_n)]^2, sobre los M pasos [TP04, p. 1]."""
    exact = exact_position(times, header["mass"], header["stiffness"], header["damping"], header["amplitude"])
    return float(np.mean((positions[1:] - exact[1:]) ** 2))
