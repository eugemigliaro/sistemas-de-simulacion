"""Estadística sobre realizaciones independientes.

Se guardan siempre el desvío estándar y el error estándar; cuál se grafica se
decide al presentar, y se explicita cómo se calculó [COR02].

- Desvío estándar σ: cuánto varía una realización de otra. No se achica con
  más realizaciones.
- Error estándar σ/√n: incertidumbre del promedio. Se achica con más
  realizaciones; es el que decide si dos configuraciones difieren.
- Media ponderada: combina valores que traen su propio error, pesando cada uno
  por 1/σᵢ².
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class Estimate:
    mean: float
    std: float
    sem: float
    count: int


def describe(values: Iterable[float]) -> Estimate:
    data = np.asarray(list(values), dtype=float)
    if data.size == 0:
        raise ValueError("no hay valores para promediar")
    if not np.all(np.isfinite(data)):
        raise ValueError("hay valores no finitos")
    if data.size == 1:
        # Con una sola realización no hay dispersión que estimar; se deja NaN
        # para no fingir una precisión que no existe.
        return Estimate(float(data[0]), math.nan, math.nan, 1)
    std = float(np.std(data, ddof=1))
    return Estimate(float(np.mean(data)), std, std / math.sqrt(data.size), int(data.size))


@dataclass(frozen=True)
class WeightedMean:
    mean: float
    error: float
    count: int


def weighted_mean(values: Iterable[float], errors: Iterable[float]) -> WeightedMean:
    """x̄ = Σ(xᵢ/σᵢ²)/Σ(1/σᵢ²), σ_x̄ = 1/√Σ(1/σᵢ²)."""
    data = np.asarray(list(values), dtype=float)
    sigma = np.asarray(list(errors), dtype=float)
    if data.size == 0 or data.shape != sigma.shape:
        raise ValueError("se necesitan tantos errores como valores")
    if not np.all(np.isfinite(sigma)) or np.any(sigma <= 0):
        raise ValueError("los errores deben ser finitos y positivos")
    weights = 1.0 / sigma**2
    return WeightedMean(
        mean=float(np.sum(weights * data) / np.sum(weights)),
        error=float(1.0 / math.sqrt(np.sum(weights))),
        count=int(data.size),
    )
