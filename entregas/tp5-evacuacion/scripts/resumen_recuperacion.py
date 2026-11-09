"""Resume el estudio de la recuperación de v_d (run_recuperacion.py): por variante, corridas
trabadas, t_evac de las que terminan, caudal J de las que llegan al 90 % de las salidas, su
diferencia con el TSDMD de la misma semilla y el costo por segundo simulado. Escribe
experiments/results/recuperacion.csv (corridas completas) y recuperacion-ventana.csv (costo
por segundo simulado en la ventana inicial, incluida la relajación analítica).

Uso: python scripts/resumen_recuperacion.py
"""
from __future__ import annotations

import csv
import math
import re

import numpy as np

from common import RAW, RESULTS
from tp5analysis.io import read_run
from tp5analysis.observables import evacuation_time, flow
from tp5analysis.stats import mean_std


def reaches(run, fraction: float = 0.9) -> bool:
    return len(run.exits) >= math.ceil(fraction * (run.agents - 1)) + 1


def window() -> None:
    folders = sorted((RAW / "recuperacion").glob("ventana*"))
    if not folders:
        return
    groups: dict[str, list] = {}
    for path in sorted(folders[0].glob("*_seed*.txt")):
        key = re.match(r"(.+)_seed\d+", path.stem).group(1)
        run = read_run(path)
        if "exited" in run.summary:
            groups.setdefault(key, []).append(run)
    rows = []
    for key in sorted(groups):
        cost = mean_std(float(r.summary["wall_seconds"]) / float(r.summary["end_time"]) for r in groups[key])
        events = mean_std(float(r.summary["events"]) / float(r.summary["end_time"]) for r in groups[key])
        rows.append({"variant": key, "window": float(groups[key][0].summary["end_time"]), "runs": len(groups[key]),
                     "cost_per_s_mean": cost[0], "cost_per_s_std": cost[1],
                     "events_per_s_mean": events[0], "events_per_s_std": events[1]})
        print(f"ventana {key:14s} costo = {cost[0] * 1e3:.2f} ± {cost[1] * 1e3:.2f} ms/s; "
              f"{events[0]:.0f} eventos/s ({len(groups[key])} corridas)")
    with open(RESULTS / "recuperacion-ventana.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    groups: dict[str, dict[int, object]] = {}
    for path in sorted((RAW / "recuperacion").glob("*_seed*.txt")):
        key, seed = re.match(r"(.+)_seed(\d+)", path.stem).groups()
        run = read_run(path)
        if "exited" in run.summary:
            groups.setdefault(key, {})[int(seed)] = run
    if "tsdmd" not in groups:
        raise SystemExit("faltan las corridas de referencia (TSDMD) en experiments/raw/recuperacion")
    reference = {seed: flow(run) for seed, run in groups["tsdmd"].items() if reaches(run)}

    def order(key: str) -> tuple[int, float]:
        for k, prefix in enumerate(("kicks", "analytic")):
            if key.startswith(prefix):
                return k, float(key.removeprefix(prefix))
        return (2, 0.0) if key == "tsdmd" else (3, 0.0)

    rows = []
    for key in sorted(groups, key=order):
        runs = groups[key]
        kind, value = order(key)
        flows = {seed: flow(run) for seed, run in runs.items() if reaches(run)}
        diff = [flows[s] - reference[s] for s in flows if s in reference]
        t_evac = mean_std(evacuation_time(r) for r in runs.values())
        j = mean_std(flows.values())
        d = mean_std(diff)
        cost = mean_std(float(r.summary["wall_seconds"]) / float(r.summary["end_time"]) for r in runs.values())
        events = mean_std(float(r.summary["events"]) / float(r.summary["end_time"]) for r in runs.values())
        rows.append({"variant": key, "kind": ("kicks", "analytic", "tsdmd", "hybrid")[kind],
                     "value": value if kind < 2 else "", "runs": len(runs),
                     "clogged": sum(1 for r in runs.values() if not r.finished),
                     "t_evac_mean": t_evac[0], "t_evac_std": t_evac[1], "finished": t_evac[2],
                     "flow_mean": j[0], "flow_std": j[1], "flow_runs": j[2],
                     "flow_diff_mean": d[0], "flow_diff_std": d[1], "paired": d[2],
                     "cost_per_s_mean": cost[0], "cost_per_s_std": cost[1],
                     "events_per_s_mean": events[0], "events_per_s_std": events[1]})
        print(f"{key:14s} trabadas {rows[-1]['clogged']}/{len(runs)}; t_evac = {t_evac[0]:.1f} ± {t_evac[1]:.1f} s "
              f"({t_evac[2]}); J = {j[0]:.3f} ± {j[1]:.3f} p/s ({j[2]}); J - J_TSDMD = {d[0]:+.3f} ± {d[1]:.3f} "
              f"({d[2]} pares); costo = {cost[0] * 1e3:.2f} ms/s; {events[0]:.0f} eventos/s")
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / "recuperacion.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    window()


if __name__ == "__main__":
    np.seterr(all="ignore")
    main()
