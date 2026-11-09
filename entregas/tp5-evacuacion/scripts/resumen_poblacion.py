"""Resume los puntos a y b (run_poblacion.py): por esquema, corridas trabadas con su
intervalo de Clopper-Pearson del 95 %, t_evac y caudal J de las que terminan, wall-clock y
eventos; las curvas de población promedio y, en el híbrido, cuántos agentes hay en cada
esquema en el tiempo. Escribe en experiments/results:
  poblacion.csv           una fila por esquema
  poblacion-corridas.csv  una fila por corrida
  poblacion-curvas.npz    grilla de tiempos, curvas de cada corrida y agentes por esquema

Uso: python scripts/resumen_poblacion.py
"""
from __future__ import annotations

import csv
import re

import numpy as np

from common import RAW, RESULTS
from tp5analysis.io import read_run
from tp5analysis.observables import evacuation_time, flow, last_exit, mode_counts, population
from tp5analysis.stats import clopper_pearson, mean_std

SCHEMES = ("tsdmd", "hybrid", "edmd", "edmd_nucleo")
STEP = 1.0           # s, grilla de las curvas de población
MODE_STEP = 0.25     # s, grilla de los agentes por esquema (el cambio ocurre en los primeros ~40 s)
MODE_HORIZON = 60.0  # s


def main() -> None:
    runs: dict[str, list] = {}
    for path in sorted((RAW / "poblacion").glob("*_seed*.txt")):
        scheme, seed = re.match(r"(.+)_seed(\d+)", path.stem).groups()
        run = read_run(path)
        if "exited" in run.summary:
            runs.setdefault(scheme, []).append((int(seed), run))
    if not runs:
        raise SystemExit("no hay corridas terminadas en experiments/raw/poblacion")

    per_run, rows = [], []
    for scheme in [s for s in SCHEMES if s in runs]:
        for seed, run in runs[scheme]:
            end = float(run.summary["end_time"])
            per_run.append({"scheme": scheme, "seed": seed, "finished": int(run.finished),
                            "exited": len(run.exits), "end_time": end, "t_evac": evacuation_time(run),
                            "last_exit": last_exit(run), "flow": flow(run) if run.finished else float("nan"),
                            "wall_seconds": float(run.summary["wall_seconds"]),
                            "events": int(run.summary["events"]), "steps": int(run.summary["steps"]),
                            "agent_steps": int(run.summary["agent_steps"])})
        group = [r for r in per_run if r["scheme"] == scheme]
        clogged = sum(1 for r in group if not r["finished"])
        low, high = clopper_pearson(clogged, len(group))
        done = [r for r in group if r["finished"]]
        t_evac = mean_std(r["t_evac"] for r in done)
        j = mean_std(r["flow"] for r in done)
        wall = mean_std(r["wall_seconds"] for r in done)
        cost = mean_std(r["wall_seconds"] / r["end_time"] for r in group)
        events = mean_std(r["events"] / r["end_time"] for r in group)
        rows.append({"scheme": scheme, "runs": len(group), "clogged": clogged, "p_clog": clogged / len(group),
                     "p_low": low, "p_high": high, "finished": t_evac[2],
                     "t_evac_mean": t_evac[0], "t_evac_std": t_evac[1], "flow_mean": j[0], "flow_std": j[1],
                     "wall_finished_mean": wall[0], "wall_finished_std": wall[1],
                     "cost_per_s_mean": cost[0], "cost_per_s_std": cost[1],
                     "events_per_s_mean": events[0], "events_per_s_std": events[1]})
        print(f"{scheme:11s} trabadas {clogged}/{len(group)} (IC 95 %: {low:.0%}–{high:.0%}); "
              f"t_evac = {t_evac[0]:.0f} ± {t_evac[1]:.0f} s y J = {j[0]:.3f} ± {j[1]:.3f} p/s "
              f"({t_evac[2]} terminan); wall = {wall[0]:.0f} ± {wall[1]:.0f} s; "
              f"costo = {cost[0] * 1e3:.1f} ms por s simulado")

    horizon = max(r["end_time"] for r in per_run)
    times = np.arange(0.0, horizon + STEP, STEP)
    mode_times = np.arange(0.0, MODE_HORIZON + MODE_STEP / 2, MODE_STEP)
    arrays: dict[str, np.ndarray] = {"times": times, "mode_times": mode_times}
    for scheme, group in runs.items():
        curves = []
        for _, run in group:
            curve = population(run, times).astype(float)
            curve[times > float(run.summary["end_time"])] = np.nan  # la corrida ya se cortó
            curves.append(curve)
        arrays[f"{scheme}_curves"] = np.array(curves)
        arrays[f"{scheme}_finished"] = np.array([run.finished for _, run in group])
        arrays[f"{scheme}_seeds"] = np.array([seed for seed, _ in group])
        if scheme == "hybrid":
            counts = [mode_counts(run, mode_times) for _, run in group]
            arrays["hybrid_event"] = np.array([c[0] for c in counts])
            arrays["hybrid_step"] = np.array([c[1] for c in counts])
            back = sum(int(np.sum(run.modes[run.modes[:, 0] > 0, 2] == 1)) for _, run in group)
            print(f"híbrido: {back} vueltas de TSDMD a EDMD en {len(group)} corridas")

    RESULTS.mkdir(parents=True, exist_ok=True)
    for name, table in (("poblacion.csv", rows), ("poblacion-corridas.csv", per_run)):
        with open(RESULTS / name, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(table[0].keys()))
            writer.writeheader()
            writer.writerows(table)
    np.savez_compressed(RESULTS / "poblacion-curvas.npz", **arrays)


if __name__ == "__main__":
    main()
