"""Resume el barrido de T* (reducido: run_tstar.py; oficial: run_tiempos.py c): por T*,
wall-clock de las que terminan, costo por segundo simulado (todas), fracción del tiempo-agente
resuelta con TSDMD, t_evac y trabadas. Elige T* por el menor costo por segundo simulado.

Uso: python scripts/resumen_tstar.py   (experiments/raw/tstar -> experiments/results/tstar.csv)
El punto c oficial lo resume resumen_tiempos.py con la misma función.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np

from common import RAW, RESULTS
from tp5analysis.io import read_run
from tp5analysis.observables import evacuation_time, exit_times
from tp5analysis.stats import mean_std


def agent_time(run) -> float:
    """Tiempo-agente adentro: integral de N_adentro(t) hasta el final de la corrida."""
    t = np.concatenate([exit_times(run), np.full(run.agents - len(run.exits), float(run.summary["end_time"]))])
    return float(t.sum())


def summarize(folder: Path, name: str) -> list[dict]:
    groups: dict[str, list] = {}
    for path in sorted(folder.glob("*_seed*.txt")):
        key = re.match(r"(.+)_seed\d+", path.stem).group(1).removeprefix("hybrid_")
        run = read_run(path)
        if "exited" in run.summary:
            groups.setdefault(key, []).append(run)

    def order(key: str) -> float:
        return float(key.removeprefix("tstar")) if key.startswith("tstar") else (1e9 if key == "tsdmd" else 2e9)

    rows = []
    for key in sorted(groups, key=order):
        runs = groups[key]
        dt = float(runs[0].params["dt"])
        wall_done = mean_std(float(r.summary["wall_seconds"]) for r in runs if r.finished)
        rate = mean_std(float(r.summary["wall_seconds"]) / float(r.summary["end_time"]) for r in runs)
        ts_fraction = mean_std(float(r.summary["agent_steps"]) * dt / agent_time(r) for r in runs
                               if r.scheme != "edmd")
        t_evac = mean_std(evacuation_time(r) for r in runs)
        rows.append({"scheme": key, "t_star": order(key) if key.startswith("tstar") else "", "runs": len(runs),
                     "clogged": sum(1 for r in runs if not r.finished),
                     "wall_finished_mean": wall_done[0], "wall_finished_std": wall_done[1], "finished": wall_done[2],
                     "cost_per_s_mean": rate[0], "cost_per_s_std": rate[1],
                     "ts_fraction_mean": ts_fraction[0], "ts_fraction_std": ts_fraction[1],
                     "t_evac_mean": t_evac[0], "t_evac_std": t_evac[1]})
        print(f"{key:12s} trabadas {rows[-1]['clogged']}/{len(runs)}; wall (terminan) = {wall_done[0]:.0f} ± "
              f"{wall_done[1]:.0f} s ({wall_done[2]}); costo = {rate[0] * 1e3:.1f} ± {rate[1] * 1e3:.1f} ms/s; "
              f"TSDMD = {ts_fraction[0]:.1%}; t_evac = {t_evac[0]:.0f} ± {t_evac[1]:.0f} s")
    hybrids = [r for r in rows if r["t_star"] != ""]
    if hybrids:
        best = min(hybrids, key=lambda r: r["cost_per_s_mean"])
        print(f"T* con menor costo por segundo simulado: {best['t_star']:g} s")
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / name, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main() -> None:
    summarize(RAW / "tstar", "tstar.csv")


if __name__ == "__main__":
    main()
