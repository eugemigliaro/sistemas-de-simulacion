"""Ajuste lineal por barrido del error E(c), como en la Teórica 0.

Dado un modelo f(x, c) se define E(c) = Σ[yᵢ − f(xᵢ, c)]² y el mejor
coeficiente es el que lo minimiza [T00, pp. 79-81]. Acá el modelo es una recta
por el origen, f(x, c) = c·x: para el DCM la ordenada es nula por definición y
el único parámetro libre es la pendiente.

El mínimo se encuentra barriendo c en una grilla y refinando alrededor del
mejor punto; no se usa la fórmula cerrada de cuadrados mínimos. Como E(c) es
plana cerca del mínimo, el barrido ubica c* con un error del orden de 1e-10
relativo, muy por debajo de la incertidumbre del ajuste. La grilla del
primer barrido se conserva para graficar E(c) con su mínimo, que la consigna
pide mostrar [TP03, p. 3].
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ProportionalFit:
    slope: float
    slope_error: float
    residual: float          # E(c*)
    points: int
    sweep_c: np.ndarray      # grilla del primer barrido, para el gráfico
    sweep_error: np.ndarray  # E(c) sobre esa grilla


def sum_squared_error(x: np.ndarray, y: np.ndarray, c: np.ndarray | float) -> np.ndarray:
    c_values = np.atleast_1d(np.asarray(c, dtype=float))
    residuals = y[np.newaxis, :] - c_values[:, np.newaxis] * x[np.newaxis, :]
    return np.sum(residuals**2, axis=1)


def fit_through_origin(
    x: np.ndarray,
    y: np.ndarray,
    grid_points: int = 401,
    refinements: int = 6,
) -> ProportionalFit:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError("x e y deben ser vectores del mismo largo")
    if x.size < 2:
        raise ValueError("se necesitan al menos dos puntos")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("hay valores no finitos")
    if np.any(x <= 0):
        raise ValueError("el ajuste por el origen requiere x > 0")
    if grid_points < 3:
        raise ValueError("grid_points debe ser al menos 3")

    # El c óptimo es un promedio de los cocientes yᵢ/xᵢ pesado por xᵢ², así
    # que está entre el menor y el mayor. Ese intervalo acota el barrido sin
    # conocer la solución de antemano; se ensancha para ver la parábola.
    ratios = y / x
    low, high = float(ratios.min()), float(ratios.max())
    span = max(high - low, abs(high) * 1e-3, 1e-12)
    low, high = low - span, high + span

    sweep_c = np.linspace(low, high, grid_points)
    sweep_error = sum_squared_error(x, y, sweep_c)

    c_values, e_values = sweep_c, sweep_error
    for _ in range(refinements):
        best = int(np.argmin(e_values))
        left = c_values[max(best - 1, 0)]
        right = c_values[min(best + 1, len(c_values) - 1)]
        c_values = np.linspace(left, right, grid_points)
        e_values = sum_squared_error(x, y, c_values)

    best = int(np.argmin(e_values))
    slope = float(c_values[best])
    residual = float(e_values[best])

    # E(c) es exactamente una parábola, E(c) = E* + (c − c*)²·Σx², con
    # curvatura E'' = 2Σx². La incertidumbre de la pendiente es
    # σ_c² = 2s²/E'', con s² = E*/(n − 1) la varianza residual: cuanto más
    # cerrada la parábola, mejor determinado queda c.
    variance = residual / (x.size - 1)
    slope_error = math.sqrt(variance / float(np.sum(x**2)))

    return ProportionalFit(
        slope=slope,
        slope_error=slope_error,
        residual=residual,
        points=int(x.size),
        sweep_c=sweep_c,
        sweep_error=sweep_error,
    )
