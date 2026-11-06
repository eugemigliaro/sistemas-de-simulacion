"""Resume el test estadístico del dt: por dt, corridas trabadas, caudal J (entre el 10 % y
el 90 % de las salidas) y t_evac de las que terminan; y la diferencia pareada de J contra
el dt más chico, con su intervalo del 95 % (t de Student). Escribe experiments/results/dt.csv.

Uso: python scripts/resumen_dt.py
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

# Cuantiles 0,975 de la t de Student (gl = 1..30), para no depender de scipy.
T975 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.160, 2.145, 2.131,
        2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]


def main() -> None:
    runs: dict[float, dict[int, object]] = {}
    for path in sorted((RAW / "dt").glob("dt*_seed*.txt")):
        dt, seed = re.match(r"dt([\d.e-]+)_seed(\d+)", path.stem).groups()
        run = read_run(path)
        if "exited" in run.summary:
            runs.setdefault(float(dt), {})[int(seed)] = run
    reference = min(runs)
    rows = []
    for dt in sorted(runs, reverse=True):
        group = runs[dt]
        clogged = sum(1 for r in group.values() if not r.finished)
        j_mean, j_std, n = mean_std(flow(r) for r in group.values())
        t_mean, t_std, t_n = mean_std(evacuation_time(r) for r in group.values())
        diffs = [flow(group[s]) - flow(runs[reference][s]) for s in group if s in runs[reference]]
        d_mean, d_std, d_n = mean_std(diffs)
        half = T975[d_n - 2] * d_std / math.sqrt(d_n) if d_n >= 2 and dt != reference else float("nan")
        rows.append({"dt": dt, "runs": len(group), "clogged": clogged, "flow_mean": j_mean, "flow_std": j_std,
                     "t_evac_mean": t_mean, "t_evac_std": t_std, "finished": t_n,
                     "flow_diff_mean": d_mean if dt != reference else 0.0, "flow_diff_half_ci95": half})
        print(f"dt = {dt * 1e3:g} ms: trabadas {clogged}/{len(group)}; J = {j_mean:.3f} ± {j_std:.3f} p/s; "
              f"t_evac = {t_mean:.0f} ± {t_std:.0f} s ({t_n} terminan)"
              + (f"; J - J(ref) = {d_mean:+.3f} ± {half:.3f} (IC 95 %)" if dt != reference else " (referencia)"))
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / "dt.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
