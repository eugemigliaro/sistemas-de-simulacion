"""Desplazamiento cuadrático medio con múltiples orígenes temporales.

La teórica pide calcular el DCM para varios tiempos dentro de la misma corrida
[T03, p. 25]. Acá cada par de cuadros guardados (tᵢ, tⱼ) aporta una muestra
con desfasaje τ = tⱼ − tᵢ: el desplazamiento cuadrático promediado sobre todas
las partículas, frescas y usadas [TP03, p. 3]. Las muestras se agrupan por τ en
intervalos de ancho fijo.

Solo se usan estados que el motor calculó en un evento. Los cuadros se guardan
cada un número entero de eventos, así que los tiempos son irregulares: por eso
se agrupa por desfasaje en lugar de pedir una grilla temporal uniforme. El
cuadro "final" se descarta porque es un avance rectilíneo hasta tmax, no un
evento; la cátedra indicó no usar estados que el motor no calcula como eventos.

Se usa el desplazamiento vectorial completo, <|Δr|²> = 4Dt en dos dimensiones
(ver wiki/dudas-y-conflictos.md).

Variante de origen único (``msd_single_origin``): el DCM en función del tiempo,
DCM(t) = <|r(t) − r(0)|²>, tal como lo define la consigna para una realización
[TP03, p. 3]. La cátedra pidió graficarlo en función del tiempo y no del
desfasaje. Los cuadros se agrupan por tiempo con los mismos intervalos, así que
el resultado usa la misma estructura ``MsdCurve``: ``lags`` es el tiempo medio
del intervalo y ``pairs`` la cantidad de cuadros que aportaron.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .trajectory import Trajectory


@dataclass(frozen=True)
class MsdCurve:
    lags: np.ndarray    # desfasaje medio de las muestras de cada intervalo
    msd: np.ndarray     # <|Δr|²> promedio del intervalo
    pairs: np.ndarray   # pares de cuadros que aportaron al intervalo
    bins: np.ndarray    # índice j del intervalo (j·ancho, (j + 1)·ancho]
    bin_width: float
    max_lag: float


def msd_multiple_origins(
    times: np.ndarray,
    positions: np.ndarray,
    bin_width: float,
    max_lag: float,
) -> MsdCurve:
    times = np.asarray(times, dtype=float)
    positions = np.asarray(positions, dtype=float)
    if positions.ndim != 3 or positions.shape[2] != 2 or positions.shape[0] != times.size:
        raise ValueError("positions debe tener forma (cuadros, partículas, 2)")
    if not (bin_width > 0 and max_lag > 0 and math.isfinite(bin_width) and math.isfinite(max_lag)):
        raise ValueError("bin_width y max_lag deben ser positivos y finitos")
    if np.any(np.diff(times) < 0):
        raise ValueError("los tiempos deben estar ordenados")

    bin_count = math.ceil(max_lag / bin_width - 1e-12)
    msd_sum = np.zeros(bin_count)
    lag_sum = np.zeros(bin_count)
    pairs = np.zeros(bin_count, dtype=np.int64)

    for offset in range(1, times.size):
        lags = times[offset:] - times[:-offset]
        # Con tiempos ordenados el menor desfasaje crece con el offset: pasado
        # max_lag, ningún offset mayor puede aportar.
        if lags.min() > max_lag:
            break
        selected = (lags > 0) & (lags <= max_lag)
        if not np.any(selected):
            continue
        displacement = positions[offset:][selected] - positions[:-offset][selected]
        squared = np.mean(np.sum(displacement**2, axis=2), axis=1)
        # Intervalo j = (j·ancho, (j + 1)·ancho].
        index = np.ceil(lags[selected] / bin_width).astype(np.int64) - 1
        index = np.clip(index, 0, bin_count - 1)
        msd_sum += np.bincount(index, weights=squared, minlength=bin_count)
        lag_sum += np.bincount(index, weights=lags[selected], minlength=bin_count)
        pairs += np.bincount(index, minlength=bin_count)

    filled = np.flatnonzero(pairs)
    return MsdCurve(
        lags=lag_sum[filled] / pairs[filled],
        msd=msd_sum[filled] / pairs[filled],
        pairs=pairs[filled],
        bins=filled,
        bin_width=float(bin_width),
        max_lag=float(max_lag),
    )


def msd_single_origin(
    times: np.ndarray,
    positions: np.ndarray,
    bin_width: float,
    max_time: float,
) -> MsdCurve:
    """DCM(t) medido desde el primer cuadro, agrupado por tiempo."""
    times = np.asarray(times, dtype=float)
    positions = np.asarray(positions, dtype=float)
    if positions.ndim != 3 or positions.shape[2] != 2 or positions.shape[0] != times.size:
        raise ValueError("positions debe tener forma (cuadros, partículas, 2)")
    if not (bin_width > 0 and max_time > 0 and math.isfinite(bin_width) and math.isfinite(max_time)):
        raise ValueError("bin_width y max_time deben ser positivos y finitos")
    if np.any(np.diff(times) < 0):
        raise ValueError("los tiempos deben estar ordenados")

    elapsed = times - times[0]
    squared = np.mean(np.sum((positions - positions[0]) ** 2, axis=2), axis=1)
    selected = (elapsed > 0) & (elapsed <= max_time)
    bin_count = math.ceil(max_time / bin_width - 1e-12)
    index = np.clip(np.ceil(elapsed[selected] / bin_width).astype(np.int64) - 1, 0, bin_count - 1)
    counts = np.bincount(index, minlength=bin_count)
    msd_sum = np.bincount(index, weights=squared[selected], minlength=bin_count)
    time_sum = np.bincount(index, weights=elapsed[selected], minlength=bin_count)
    filled = np.flatnonzero(counts)
    return MsdCurve(
        lags=time_sum[filled] / counts[filled],
        msd=msd_sum[filled] / counts[filled],
        pairs=counts[filled],
        bins=filled,
        bin_width=float(bin_width),
        max_lag=float(max_time),
    )


def trajectory_msd(
    trajectory: Trajectory,
    bin_width: float,
    max_lag: float,
    start_time: float = 0.0,
    single_origin: bool = False,
) -> MsdCurve:
    """DCM de una realización, usando solo cuadros que son eventos.

    Con ``single_origin`` devuelve DCM(t) desde ``start_time``; si no, el DCM
    con múltiples orígenes en función del desfasaje.
    """
    keep = np.array([reason != "final" for reason in trajectory.reasons])
    keep &= trajectory.times >= start_time
    times = trajectory.times[keep]
    positions = trajectory.positions[keep]

    # Eventos simultáneos dejan cuadros con el mismo tiempo y las mismas
    # posiciones; basta uno.
    unique = np.concatenate(([True], np.diff(times) > 0))
    times, positions = times[unique], positions[unique]
    if times.size < 2:
        raise ValueError("no hay suficientes cuadros para el DCM")
    if single_origin:
        return msd_single_origin(times, positions, bin_width, max_lag)
    return msd_multiple_origins(times, positions, bin_width, max_lag)
