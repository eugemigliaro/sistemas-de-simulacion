"""Fu y promedios por posicion: primero observable por realizacion, luego agregado."""
import numpy as np


def used_fraction(first_contacts, dt, time_grid):
    contacts = np.asarray(first_contacts, dtype=float)
    if contacts.ndim != 1 or not len(contacts) or not np.isfinite(contacts).all():
        raise ValueError("Contactos invalidos")
    if np.any(contacts < -1) or np.any(contacts != np.floor(contacts)) or dt <= 0:
        raise ValueError("Pasos de contacto invalidos")
    times = np.sort(contacts[contacts >= 0] * dt)
    return np.searchsorted(times, time_grid, side="right") / len(contacts)


def summarize_positions(cases):
    rows = []
    for n, x in sorted({(c["n"], c["obstacle_x"]) for c in cases}):
        group = [c for c in cases if c["n"] == n and c["obstacle_x"] == x]
        observed = [c["conversion"]["t90_s"] for c in group if c["conversion"]["t90_s"] is not None]
        complete = len(observed) == len(group)
        rows.append(dict(n=n, obstacle_x_m=x, repetitions=len(group), censored=len(group)-len(observed),
            t90_mean_s=float(np.mean(observed)) if complete else None,
            t90_std_s=float(np.std(observed, ddof=1)) if complete and len(observed)>1 else None,
            t90_observed_mean_s=float(np.mean(observed)) if observed else None,
            t90_mean_lower_bound_s=float(np.mean([c["conversion"]["t90_s"] if c["conversion"]["t90_s"] is not None
                                                else c["duration"] for c in group])),
            fu_final_mean=float(np.mean([c["conversion"]["fu_final"] for c in group])),
            fu_final_std=float(np.std([c["conversion"]["fu_final"] for c in group], ddof=1))))
    return rows
