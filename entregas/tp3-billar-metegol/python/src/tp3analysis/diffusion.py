"""Coeficiente de difusión a partir del DCM.

En dos dimensiones <|Δr|²> = 4Dt, así que D es un cuarto de la pendiente del
ajuste por el origen. El ajuste se hace dentro de una ventana [t_a, t_b] fija,
la misma para todas las configuraciones: antes el movimiento es balístico y
después el DCM satura por las paredes.

Con varias realizaciones se calculan tres estimaciones, para elegir al
presentar y verificar que sean compatibles:

1. media ± σ y ± σ/√n de los D de cada realización;
2. media ponderada por el error del ajuste de cada realización. Ese error sale
   de los residuos, y los puntos de un DCM con múltiples orígenes están
   correlacionados, así que tiende a ser optimista;
3. un único ajuste sobre el DCM promediado entre realizaciones, como sugiere la
   teórica ("varios DCM ... en la misma corrida y en varias corridas")
   [T03, p. 25].
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .fit import ProportionalFit, fit_through_origin
from .msd import MsdCurve
from .stats import Estimate, WeightedMean, describe, weighted_mean


DIMENSIONS = 2


@dataclass(frozen=True)
class DiffusionFit:
    coefficient: float
    error: float
    window: tuple[float, float]
    fit: ProportionalFit


@dataclass(frozen=True)
class PooledMsd:
    lags: np.ndarray
    msd: np.ndarray
    std: np.ndarray        # dispersión entre realizaciones en cada intervalo
    realizations: int


@dataclass(frozen=True)
class DiffusionSummary:
    per_run: tuple[DiffusionFit, ...]
    plain: Estimate
    weighted: WeightedMean
    pooled: DiffusionFit
    pooled_curve: PooledMsd


def _validate_window(window: tuple[float, float]) -> tuple[float, float]:
    start, end = (float(value) for value in window)
    if not 0 <= start < end:
        raise ValueError("la ventana debe cumplir 0 <= t_a < t_b")
    return start, end


def fit_window(lags: np.ndarray, msd: np.ndarray, window: tuple[float, float]) -> DiffusionFit:
    start, end = _validate_window(window)
    selected = (lags >= start) & (lags <= end)
    if np.count_nonzero(selected) < 2:
        raise ValueError(f"menos de dos puntos del DCM en la ventana {window}")
    fit = fit_through_origin(lags[selected], msd[selected])
    scale = 2 * DIMENSIONS
    return DiffusionFit(
        coefficient=fit.slope / scale,
        error=fit.slope_error / scale,
        window=(start, end),
        fit=fit,
    )


def fit_diffusion(curve: MsdCurve, window: tuple[float, float]) -> DiffusionFit:
    return fit_window(curve.lags, curve.msd, window)


def pool_curves(curves: list[MsdCurve]) -> PooledMsd:
    if not curves:
        raise ValueError("no hay curvas para promediar")
    first = curves[0]
    for curve in curves[1:]:
        if curve.bin_width != first.bin_width or curve.max_lag != first.max_lag:
            raise ValueError("las curvas deben usar los mismos intervalos")

    # Solo intervalos presentes en todas las realizaciones, para que cada
    # punto promedie la misma cantidad de corridas.
    common = first.bins
    for curve in curves[1:]:
        common = np.intersect1d(common, curve.bins)
    if common.size == 0:
        raise ValueError("las curvas no tienen intervalos en común")

    def pick(curve: MsdCurve, values: np.ndarray) -> np.ndarray:
        return values[np.searchsorted(curve.bins, common)]

    lags = np.array([pick(curve, curve.lags) for curve in curves])
    msd = np.array([pick(curve, curve.msd) for curve in curves])
    std = msd.std(axis=0, ddof=1) if len(curves) > 1 else np.full(common.size, np.nan)
    return PooledMsd(
        lags=lags.mean(axis=0),
        msd=msd.mean(axis=0),
        std=std,
        realizations=len(curves),
    )


def summarize_diffusion(curves: list[MsdCurve], window: tuple[float, float]) -> DiffusionSummary:
    per_run = tuple(fit_diffusion(curve, window) for curve in curves)
    pooled_curve = pool_curves(curves)
    return DiffusionSummary(
        per_run=per_run,
        plain=describe(fit.coefficient for fit in per_run),
        weighted=weighted_mean(
            [fit.coefficient for fit in per_run],
            [fit.error for fit in per_run],
        ),
        pooled=fit_window(pooled_curve.lags, pooled_curve.msd, window),
        pooled_curve=pooled_curve,
    )
