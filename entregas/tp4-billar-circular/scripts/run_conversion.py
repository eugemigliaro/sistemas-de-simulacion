#!/usr/bin/env python3
"""Fracción de partículas usadas: posición de los obstáculos (2.2), densidad
(2.4.a) y mapa posición-densidad (2.4.b) [TP04, pp. 3-4].

Uso: run_conversion.py <position|density|map>

Por realización se calculan Fu(t), t90, t100 y Fu(tf); el promedio y el
desvío se toman después, entre realizaciones.
"""
import sys

import numpy as np

from common import COUNTS, PARTICLE_RADIUS, POSITIONS, RAW, RESULTS, SEEDS, billiard, parallel, require_engine, \
    write_csv
from tp4analysis import conversion, files, stats

# Estudio -> (casos (N, x0), tf, intervalo de salida).
STUDIES = {
    "position": ([(n, x0) for n in (100, 20) for x0 in POSITIONS], 100.0, 0.05),
    # Las mismas corridas de 2.1.b (N, x0 = r, semillas y dt), continuadas
    # hasta 300 s para que las densidades altas lleguen a Fu = 0,9.
    "density": ([(n, PARTICLE_RADIUS) for n in COUNTS], 300.0, 0.1),
    # 2.4.b: completa las densidades de 2.2 con N = 50 y N = 200.
    "map": ([(n, x0) for n in (50, 200) for x0 in POSITIONS], 100.0, 0.05),
}


def run(case: tuple[str, int, float, int]) -> dict:
    study, n, x0, seed = case
    _, tf, interval = STUDIES[study]
    path = billiard(RAW / study / f"n{n}-x{x0:g}-s{seed}.txt", n, tf, interval, seed, x0=x0)
    summary = conversion.summarize_run(files.read_billiard(path))
    return {"n": n, "x0_m": x0, "seed": seed, "t90_s": summary["t90"], "t100_s": summary["t100"],
            "fu_final": summary["fu_final"], "times": summary["times"], "fu": summary["fu"]}


def aggregate(runs: list[dict]) -> list[dict]:
    rows = []
    for n, x0 in dict.fromkeys((r["n"], r["x0_m"]) for r in runs):
        group = [r for r in runs if (r["n"], r["x0_m"]) == (n, x0)]
        t90 = stats.censored_mean([r["t90_s"] for r in group])
        t100 = stats.censored_mean([r["t100_s"] for r in group])
        fu_mean, fu_std = stats.mean_and_std([r["fu_final"] for r in group])
        rows.append({"n": n, "x0_m": x0, "realizations": len(group),
                     "t90_mean_s": t90["mean"], "t90_std_s": t90["std"], "t90_missing": t90["missing"],
                     "t100_mean_s": t100["mean"], "t100_std_s": t100["std"], "t100_missing": t100["missing"],
                     "fu_final_mean": fu_mean, "fu_final_std": fu_std})
    return rows


def main() -> None:
    study = sys.argv[1] if len(sys.argv) == 2 else ""
    if study not in STUDIES:
        raise SystemExit(f"uso: run_conversion.py <{'|'.join(STUDIES)}>")
    require_engine()
    cases, _, _ = STUDIES[study]
    runs = parallel(run, [(study, n, x0, seed) for n, x0 in cases for seed in SEEDS])
    write_csv(RESULTS / f"{study}-runs.csv",
              [{k: r[k] for k in ("n", "x0_m", "seed", "t90_s", "t100_s", "fu_final")} for r in runs])
    summary = aggregate(runs)
    write_csv(RESULTS / f"{study}-summary.csv", summary)
    np.savez_compressed(RESULTS / f"{study}-fu.npz", times=runs[0]["times"],
                        n=np.array([r["n"] for r in runs]), x0=np.array([r["x0_m"] for r in runs]),
                        seed=np.array([r["seed"] for r in runs]), fu=np.array([r["fu"] for r in runs]))
    for row in summary:
        print(f"N={row['n']:3d} x0={row['x0_m']:.4f}  t90={row['t90_mean_s']} +- {row['t90_std_s']} "
              f"(sin llegar {row['t90_missing']})  Fu(tf)={row['fu_final_mean']:.3f}")


if __name__ == "__main__":
    main()
