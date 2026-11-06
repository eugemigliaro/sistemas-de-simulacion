"""Puntos a y b: los tres esquemas con N = 500, las mismas 20 semillas (401 a 420).
Además, una corrida con cuadros por esquema para las animaciones (semilla 401).

Uso: python scripts/run_poblacion.py
"""
from common import DT, RAW, SECOND_TARGET, T_STAR, evacuate, run_all

SEEDS = range(401, 421)
SCHEMES = {"tsdmd": {}, "hybrid": {"t_star": T_STAR}, "edmd": {}}


def main() -> None:
    jobs = []
    for name, extra in SCHEMES.items():
        for seed in SEEDS:
            path = RAW / "poblacion" / f"{name}_seed{seed}.txt"
            jobs.append((path, evacuate(path, scheme=name, dt=DT, seed=seed, **SECOND_TARGET, **extra)))
        path = RAW / "animaciones" / f"{name}_seed401.txt"
        jobs.append((path, evacuate(path, scheme=name, dt=DT, seed=401, output_dt=0.1, **SECOND_TARGET, **extra)))
    run_all(jobs)


if __name__ == "__main__":
    main()
