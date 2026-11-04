"""Promedios entre realizaciones. La barra de error es el desvío estándar muestral entre
realizaciones (ddof = 1) [T00, p. 69]; cada realización aporta un único valor por observable."""
from __future__ import annotations

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
