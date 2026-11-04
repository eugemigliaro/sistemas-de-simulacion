"""Observables de una corrida: curva de población, tiempo de evacuación, caudal y modos."""
from __future__ import annotations

import numpy as np

from .io import Run


def exit_times(run: Run) -> np.ndarray:
    return np.sort(run.exits[:, 0]) if len(run.exits) else np.zeros(0)


def population(run: Run, times: np.ndarray) -> np.ndarray:
    """Agentes adentro en cada instante: N menos los que salieron hasta t [T05, p. 21]."""
    return run.agents - np.searchsorted(exit_times(run), times, side="right")


def evacuation_time(run: Run) -> float:
    """Instante en que sale el último agente; NaN si la corrida no terminó (atasco o corte)."""
    return float(exit_times(run)[-1]) if run.finished and len(run.exits) else float("nan")


def last_exit(run: Run) -> float:
    t = exit_times(run)
    return float(t[-1]) if len(t) else float("nan")


def flow(run: Run, low: float = 0.1, high: float = 0.9) -> float:
    """Caudal medio [agentes/s] entre el low y el high de las salidas (tramo casi recto
    de la curva de población): (k_high - k_low) / (t_high - t_low)."""
    t = exit_times(run)
    if len(t) < 3:
        return float("nan")
    a = int(np.floor(low * (run.agents - 1)))
    b = int(np.ceil(high * (run.agents - 1)))
    b = min(b, len(t) - 1)
    if b <= a:
        return float("nan")
    return (b - a) / (t[b] - t[a])


def largest_gap(run: Run) -> float:
    """Mayor tiempo entre dos salidas consecutivas (duración del atasco más largo que se rompió)."""
    t = exit_times(run)
    return float(np.max(np.diff(t))) if len(t) > 1 else float("nan")


def mode_counts(run: Run, times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Agentes adentro en EDMD y en TSDMD en cada instante, reconstruidos a partir de los
    cambios de modo y las salidas. Con un esquema puro, todos en su esquema."""
    n = run.agents
    if len(run.modes) == 0:
        inside = population(run, times)
        if run.scheme == "edmd":
            return inside, np.zeros_like(inside)
        return np.zeros_like(inside), inside
    events = [(t, 0, int(i), int(m)) for t, i, m in run.modes]
    events += [(t, 1, int(i), -1) for t, i in run.exits]
    events.sort()
    mode = np.full(n, -1)
    ed = ts = 0
    out_ed = np.zeros(len(times), dtype=int)
    out_ts = np.zeros(len(times), dtype=int)
    k = 0
    for idx, t in enumerate(times):
        while k < len(events) and events[k][0] <= t:
            _, kind, i, m = events[k]
            if mode[i] == 1:
                ed -= 1
            elif mode[i] == 0:
                ts -= 1
            if kind == 0:
                mode[i] = m
                if m == 1:
                    ed += 1
                else:
                    ts += 1
            else:
                mode[i] = -2  # salió
            k += 1
        out_ed[idx] = ed
        out_ts[idx] = ts
    return out_ed, out_ts


def summary_value(run: Run, key: str) -> float:
    return float(run.summary.get(key, float("nan")))
