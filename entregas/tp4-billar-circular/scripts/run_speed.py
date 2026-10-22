#!/usr/bin/env python3
"""2.3: distribución del módulo de la velocidad con N = 100 y billar vacío [TP04, p. 4].

f(v) se estima con histogramas normalizados: en cada instante, con las N
partículas de las 30 realizaciones; en el estacionario, promediando entre
realizaciones los histogramas de todos los cuadros de cada una. kBT se ajusta
con el método de la Teórica 0 y se compara con m<v^2>/2.
"""
import numpy as np

from common import RAW, RESULTS, billiard, parallel, require_engine, write_csv, write_json
from tp4analysis import energy, files, speed, stats

N = 100
# Más realizaciones que en los otros estudios: cada instante de la evolución
# solo tiene N rapideces por realización.
SEEDS = list(range(1, 31))
TF = 60.0
INTERVAL = 0.05
MASS = 0.025
INITIAL_SPEED = 1.0
# Bins de 0,1 m/s centrados en múltiplos de 0,1: v0 = 1 m/s cae en el centro de un bin.
EDGES = np.concatenate([[0.0], np.arange(0.05, 5.0, 0.1)])
CENTERS = np.concatenate([[0.025], np.arange(0.1, 4.95, 0.1)])
SNAPSHOTS = [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]
WINDOW = 1.0


def run(seed: int) -> dict:
    path = billiard(RAW / "speed" / f"s{seed}.txt", N, TF, INTERVAL, seed)
    trajectory = files.read_billiard(path)
    total = energy.total_energy(trajectory)
    kinetic = 0.5 * MASS * np.sum(trajectory.velocities**2, axis=(1, 2))
    return {"seed": seed, "times": trajectory.times,
            "speeds": np.linalg.norm(trajectory.velocities, axis=2).astype(np.float64),
            "kinetic": kinetic / N, "potential": (total - kinetic) / N}


def thermal_energy(density: np.ndarray) -> float:
    best, _, _ = speed.fit_thermal_energy(CENTERS, density, MASS, 1e-3, 5e-2)
    return best


def main() -> None:
    require_engine()
    runs = parallel(run, SEEDS)
    times = runs[0]["times"]
    speeds = np.stack([r["speeds"] for r in runs])  # (realizaciones, cuadros, N)

    # Evolución: histogramas en algunos instantes, con las N x realizaciones partículas.
    evolution = []
    for t in SNAPSHOTS:
        frame = int(np.argmin(np.abs(times - t)))
        density = speed.probability_density(speeds[:, frame].ravel(), EDGES)
        evolution += [{"t_s": t, "v_m_s": v, "density_s_m": f} for v, f in zip(CENTERS, density)]
    write_csv(RESULTS / "speed-evolution.csv", evolution)

    # Ventanas de 1 s: kBT ajustado en cada una, para ubicar el estacionario.
    windows = []
    for start in np.arange(0.0, TF, WINDOW):
        frames = (times >= start) & (times < start + WINDOW)
        density = speed.probability_density(speeds[:, frames].ravel(), EDGES)
        windows.append({"start_s": float(start), "kbt_j": thermal_energy(density)})
    write_csv(RESULTS / "speed-windows.csv", windows)
    late = np.array([w["kbt_j"] for w in windows if w["start_s"] >= TF / 2])
    band = late.mean() + 3 * late.std(ddof=1) * np.array([-1, 1])
    stationary_start = next(w["start_s"] for i, w in enumerate(windows)
                            if all(band[0] <= x["kbt_j"] <= band[1] for x in windows[i:]))

    # Estacionario: histograma de cada realización y promedio entre realizaciones.
    frames = times >= stationary_start
    per_run = np.array([speed.probability_density(s[frames].ravel(), EDGES) for s in speeds])
    density_mean = per_run.mean(axis=0)
    density_std = per_run.std(axis=0, ddof=1)
    write_csv(RESULTS / "speed-stationary.csv",
              [{"v_m_s": v, "density_mean_s_m": f, "density_std_s_m": s}
               for v, f, s in zip(CENTERS, density_mean, density_std)])
    best, grid, errors = speed.fit_thermal_energy(CENTERS, density_mean, MASS, 1e-3, 5e-2)
    write_csv(RESULTS / "speed-fit-error.csv", [{"kbt_j": k, "error": e} for k, e in zip(grid, errors)])
    per_run_fit = [thermal_energy(d) for d in per_run]
    kinetic = [r["kinetic"][frames].mean() for r in runs]
    potential = [r["potential"][frames].mean() for r in runs]
    summary = {
        "stationary_start_s": stationary_start,
        "kbt_j": best,
        "kbt_per_realization_std_j": stats.mean_and_std(per_run_fit)[1],
        "mean_kinetic_energy_j": stats.mean_and_std(kinetic)[0],
        "mean_kinetic_energy_std_j": stats.mean_and_std(kinetic)[1],
        "mean_potential_energy_j": stats.mean_and_std(potential)[0],
        "initial_kinetic_energy_j": 0.5 * MASS * INITIAL_SPEED**2,
        "realizations": len(runs),
        "samples": int(frames.sum()) * N * len(runs),
    }
    write_json(RESULTS / "speed-summary.json", summary)
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
