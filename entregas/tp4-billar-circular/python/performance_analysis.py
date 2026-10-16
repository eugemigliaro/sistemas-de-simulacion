"""Estadistica del benchmark y tiempos de conversion desde estado historico."""
import math

import numpy as np


def conversion_times(state, dt, cutoff):
    contacts = state[:, 8]
    valid = contacts[contacts >= 0] * dt
    if np.any(valid > cutoff + 1e-9):
        raise ValueError("Contacto fuera del horizonte")
    n = len(contacts)
    k90 = math.ceil(.9 * n)
    valid.sort()
    return dict(t90_s=float(valid[k90 - 1]) if len(valid) >= k90 else None,
                t100_s=float(valid[-1]) if len(valid) == n else None,
                fu_final=len(valid) / n)


def summarize(cases):
    rows = []
    for engine, n in sorted({(c["engine"], c["n"]) for c in cases}):
        group = [c for c in cases if c["engine"] == engine and c["n"] == n]
        values = [c["runtime_seconds"] for c in group]
        row = dict(engine=engine, n=n, repetitions=len(group), runtime_mean_s=float(np.mean(values)),
                   runtime_std_s=float(np.std(values, ddof=1)) if len(values) > 1 else 0)
        rows.append(row)
    return rows


def summarize_density(cases, radius=.51):
    rows = []
    for n in sorted({c["n"] for c in cases if c["engine"] == "tp4"}):
        group = [c for c in cases if c["engine"] == "tp4" and c["n"] == n]
        row = dict(n=n, density_m2=n / (math.pi * radius**2), repetitions=len(group),
                   fu_final_mean=float(np.mean([c["conversion"]["fu_final"] for c in group])))
        for observable in ["t90", "t100"]:
            times = [c["conversion"][observable + "_s"] for c in group]
            observed = [t for t in times if t is not None]
            row[observable + "_censored"] = len(times) - len(observed)
            # Media ordinaria solo cuando todas las realizaciones alcanzaron el umbral.
            row[observable + "_mean_s"] = float(np.mean(observed)) if len(observed) == len(times) else None
            row[observable + "_std_s"] = float(np.std(observed, ddof=1)) if len(observed) == len(times) and len(times) > 1 else None
            row[observable + "_observed_mean_s"] = float(np.mean(observed)) if observed else None
            row[observable + "_mean_lower_bound_s"] = float(np.mean([
                t if t is not None else c["final_time"] for t, c in zip(times, group)]))
        rows.append(row)
    return rows
