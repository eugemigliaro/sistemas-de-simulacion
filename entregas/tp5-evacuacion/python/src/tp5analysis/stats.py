"""Promedios entre realizaciones. La barra de error es el desvío estándar muestral entre
realizaciones (ddof = 1) [T00, p. 69]; cada realización aporta un único valor por observable."""
from __future__ import annotations

import math

import numpy as np


def mean_std(values) -> tuple[float, float, int]:
    v = np.asarray([x for x in values if np.isfinite(x)], dtype=float)
    if len(v) == 0:
        return float("nan"), float("nan"), 0
    return float(v.mean()), float(v.std(ddof=1)) if len(v) > 1 else 0.0, len(v)


def band(curves: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Media y desvío punto a punto de curvas sobre una grilla común (filas = realizaciones)."""
    c = np.asarray(curves, dtype=float)
    return c.mean(axis=0), c.std(axis=0, ddof=1) if len(c) > 1 else np.zeros(c.shape[1])


def binomial_tail(k: int, n: int, p: float) -> float:
    """P(X >= k) con X ~ Binomial(n, p)."""
    return sum(math.comb(n, j) * p**j * (1 - p) ** (n - j) for j in range(k, n + 1))


def clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Intervalo exacto para una proporción binomial (k éxitos en n), por bisección."""
    alpha = 1 - level

    def solve(f, target):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if f(mid) < target:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    low = 0.0 if k == 0 else solve(lambda p: binomial_tail(k, n, p), alpha / 2)
    # P(X <= k) = alpha/2  <=>  P(X >= k + 1) = 1 - alpha/2, creciente en p.
    high = 1.0 if k == n else solve(lambda p: binomial_tail(k + 1, n, p), 1 - alpha / 2)
    return low, high
