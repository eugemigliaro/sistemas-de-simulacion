"""Resume los tiempos de ejecución de run_tiempos.py (puntos c y d, medidos en una sola
computadora). Escribe experiments/results/tiempos-c.csv (una fila por T*, más TSDMD y EDMD,
con las mismas columnas que tstar.csv) o tiempos-d.csv (una fila por variante, N y esquema).

Para c escribe además tiempos-c-pareado.csv: cada corrida comparada con el TSDMD de la misma
semilla (mismas condiciones iniciales). El costo por segundo simulado se compara en las 10
semillas; el wall-clock, solo en las que terminan las dos.

Uso: python scripts/resumen_tiempos.py c|d
"""
from __future__ import annotations

import csv
import re
import sys

import numpy as np

from common import AGENTS, RAW, RESULTS
from resumen_tstar import summarize
from tp5analysis.io import read_run
from tp5analysis.observables import evacuation_time
from tp5analysis.stats import mean_std

SCHEMES = ("tsdmd", "hybrid", "edmd")
FOLDER = RAW / "tiempos" / f"base{AGENTS}"  # la de run_tiempos.py


def point_d() -> None:
    groups: dict[tuple[str, int, str], list] = {}
    for path in sorted((FOLDER / "d").glob("*_seed*.txt")):
        variant, n, scheme = re.match(r"(\w+?)_n(\d+)_(\w+)_seed\d+", path.stem).groups()
        run = read_run(path)
        if "exited" in run.summary:
            groups.setdefault((variant, int(n), scheme), []).append(run)
    if not groups:
        raise SystemExit(f"no hay corridas terminadas en {FOLDER / 'd'}")
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


def paired_c() -> None:
    runs: dict[str, dict[int, object]] = {}
    for path in sorted((FOLDER / "c").glob("*_seed*.txt")):
        key, seed = re.match(r"(.+)_seed(\d+)", path.stem).groups()
        run = read_run(path)
        if "exited" in run.summary:
            runs.setdefault(key.removeprefix("hybrid_"), {})[int(seed)] = run
    reference = runs.get("tsdmd", {})

    def cost(run) -> float:
        return float(run.summary["wall_seconds"]) / float(run.summary["end_time"])

    rows = []
    for key, group in runs.items():
        if key == "tsdmd":
            continue
        seeds = [s for s in group if s in reference]
        ratio = mean_std(cost(group[s]) / cost(reference[s]) for s in seeds)
        both = [s for s in seeds if group[s].finished and reference[s].finished]
        wall = mean_std(float(group[s].summary["wall_seconds"]) / float(reference[s].summary["wall_seconds"])
                        for s in both)
        same = sum(1 for s in seeds if np.array_equal(group[s].exits, reference[s].exits))
        rows.append({"config": key, "t_star": float(key.removeprefix("tstar")) if key.startswith("tstar") else "",
                     "cost_ratio_mean": ratio[0], "cost_ratio_std": ratio[1], "pairs": ratio[2],
                     "wall_ratio_mean": wall[0], "wall_ratio_std": wall[1], "both_finished": wall[2],
                     "same_exits": same})
        print(f"{key:12s} costo / TSDMD = {ratio[0]:.3f} ± {ratio[1]:.3f} ({ratio[2]} semillas); "
              f"wall / TSDMD = {wall[0]:.3f} ± {wall[1]:.3f} ({wall[2]} terminan las dos); "
              f"mismas salidas que TSDMD: {same}")
    rows.sort(key=lambda r: r["t_star"] if r["t_star"] != "" else float("inf"))
    with open(RESULTS / "tiempos-c-pareado.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what == "c":
        summarize(FOLDER / "c", "tiempos-c.csv")
        paired_c()
    elif what == "d":
        point_d()
    else:
        raise SystemExit("uso: resumen_tiempos.py c|d")


if __name__ == "__main__":
    main()
