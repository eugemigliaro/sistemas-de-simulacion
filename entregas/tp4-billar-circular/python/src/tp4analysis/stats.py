"""Promedios entre realizaciones independientes."""
from __future__ import annotations

import numpy as np


def mean_and_std(values) -> tuple[float, float]:
    """Media y desvío estándar muestral (n - 1) entre realizaciones."""
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        raise ValueError("no hay realizaciones")
    std = float(np.std(values, ddof=1)) if values.size > 1 else 0.0
    return float(np.mean(values)), std


def censored_mean(values) -> dict:
    """Resume tiempos que pueden faltar (None: la realización no llegó).

    La media y el desvío solo se informan si llegaron todas las realizaciones;
    si no, se informa cuántas no llegaron.
    """
    observed = [v for v in values if v is not None]
    summary = {"realizations": len(values), "missing": len(values) - len(observed), "mean": None, "std": None}
    if observed and len(observed) == len(values):
        summary["mean"], summary["std"] = mean_and_std(observed)
    return summary


def significant(value: float, error: float) -> tuple[str, str]:
    """Redondea el error a una cifra significativa (dos si empieza con 1) y el
    valor a la misma posición decimal [T00]."""
    if error <= 0 or not np.isfinite(error):
        return f"{value:.3g}", "0"
    exponent = int(np.floor(np.log10(error)))
    digits = 2 if int(error / 10**exponent) == 1 else 1
    decimals = max(0, digits - 1 - exponent)
    return f"{value:.{decimals}f}", f"{error:.{decimals}f}"
