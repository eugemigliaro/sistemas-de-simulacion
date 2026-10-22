#!/usr/bin/env python3
"""2.1.a: conservación de la energía con N = 300 y billar vacío, para elegir dt [TP04, p. 3].

Observable: delta_E = max_t |E(t) - E(0)| / E(0) sobre todo el horizonte, que
es el de las corridas más largas del trabajo (300 s).
"""
import numpy as np

from common import RAW, RESULTS, billiard, diverged, parallel, require_engine, write_csv
from tp4analysis import energy, files, stats

N = 300
STEPS = [5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5]
SEEDS = [1, 2, 3, 4, 5]
TF = 300.0
INTERVAL = 0.1


def run(case: tuple[float, int]) -> dict:
    dt, seed = case
    path = billiard(RAW / "energy" / f"dt{dt:g}-s{seed}.txt", N, TF, INTERVAL, seed, dt=dt, allow_divergence=True)
    trajectory = files.read_billiard(path, truncated=diverged(path))
    deviation = np.full(int(round(TF / INTERVAL)) + 1, np.nan)
    deviation[:len(trajectory.times)] = energy.relative_deviation(energy.total_energy(trajectory))
    return {"dt": dt, "seed": seed, "diverged": diverged(path), "last_time": float(trajectory.times[-1]),
            "deviation": deviation}


def main() -> None:
    require_engine()
    cases = [(dt, seed) for dt in sorted(STEPS) for seed in SEEDS]
    runs = parallel(run, cases)
    write_csv(RESULTS / "energy-runs.csv",
              [{"dt_s": r["dt"], "seed": r["seed"], "diverged": r["diverged"], "last_time_s": r["last_time"],
                "delta_e": None if r["diverged"] else float(np.max(r["deviation"]))} for r in runs])
    summary = []
    for dt in sorted(STEPS):
        group = [r for r in runs if r["dt"] == dt]
        row = {"dt_s": dt, "realizations": len(group), "diverged": sum(r["diverged"] for r in group),
               "delta_e_mean": None, "delta_e_std": None}
        if not row["diverged"]:
            row["delta_e_mean"], row["delta_e_std"] = stats.mean_and_std([np.max(r["deviation"]) for r in group])
        summary.append(row)
        print(row)
    write_csv(RESULTS / "energy-summary.csv", summary)
    first_seed = [r for r in runs if r["seed"] == SEEDS[0]]
    np.savez_compressed(RESULTS / "energy-series.npz", times=np.arange(len(first_seed[0]["deviation"])) * INTERVAL,
                        steps=np.array([r["dt"] for r in first_seed]),
                        deviation=np.array([r["deviation"] for r in first_seed]))


if __name__ == "__main__":
    main()
