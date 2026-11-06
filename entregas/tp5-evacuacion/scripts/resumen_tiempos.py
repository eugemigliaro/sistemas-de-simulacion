"""Resume los tiempos de ejecución de run_tiempos.py (puntos c y d, medidos en una sola
computadora). Escribe experiments/results/tiempos-c.csv (una fila por T*, más TSDMD y EDMD,
con las mismas columnas que tstar.csv) o tiempos-d.csv (una fila por variante, N y esquema).

Uso: python scripts/resumen_tiempos.py c|d
"""
from __future__ import annotations

import csv
import re
import sys

from common import RAW, RESULTS
from resumen_tstar import summarize
from tp5analysis.io import read_run
from tp5analysis.observables import evacuation_time
from tp5analysis.stats import mean_std

SCHEMES = ("tsdmd", "hybrid", "edmd")


def point_d() -> None:
    groups: dict[tuple[str, int, str], list] = {}
    for path in sorted((RAW / "tiempos" / "d").glob("*_seed*.txt")):
        variant, n, scheme = re.match(r"(\w+?)_n(\d+)_(\w+)_seed\d+", path.stem).groups()
        run = read_run(path)
        if "exited" in run.summary:
            groups.setdefault((variant, int(n), scheme), []).append(run)
    if not groups:
        raise SystemExit("no hay corridas terminadas en experiments/raw/tiempos/d")
    rows = []
    for variant, n, scheme in sorted(groups, key=lambda k: (k[0], k[1], SCHEMES.index(k[2]))):
        runs = groups[(variant, n, scheme)]
        wall = mean_std(float(r.summary["wall_seconds"]) for r in runs if r.finished)
        cost = mean_std(float(r.summary["wall_seconds"]) / float(r.summary["end_time"]) for r in runs)
        t_evac = mean_std(evacuation_time(r) for r in runs)
        rows.append({"variant": variant, "agents": n, "side": float(runs[0].params["side"]), "scheme": scheme,
                     "runs": len(runs), "clogged": sum(1 for r in runs if not r.finished),
                     "wall_finished_mean": wall[0], "wall_finished_std": wall[1], "finished": wall[2],
                     "cost_per_s_mean": cost[0], "cost_per_s_std": cost[1],
                     "t_evac_mean": t_evac[0], "t_evac_std": t_evac[1]})
        print(f"{variant:8s} N = {n:4d} {scheme:6s} trabadas {rows[-1]['clogged']}/{len(runs)}; "
              f"wall (terminan) = {wall[0]:.0f} ± {wall[1]:.0f} s ({wall[2]}); "
              f"costo = {cost[0] * 1e3:.1f} ± {cost[1] * 1e3:.1f} ms/s")
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / "tiempos-d.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what == "c":
        summarize(RAW / "tiempos" / "c", "tiempos-c.csv")
    elif what == "d":
        point_d()
    else:
        raise SystemExit("uso: resumen_tiempos.py c|d")


if __name__ == "__main__":
    main()
