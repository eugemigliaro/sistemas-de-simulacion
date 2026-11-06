"""Punto c reducido, solo para elegir T* en esta computadora (el oficial es run_tiempos.py):
híbrido con cada T* de T_STARS, N = 500, semillas 501 a 505.

Uso: python scripts/run_tstar.py
"""
from common import DT, RAW, SECOND_TARGET, T_STARS, evacuate, run_all

SEEDS = range(501, 506)


def main() -> None:
    jobs = []
    for t_star in T_STARS:
        for seed in SEEDS:
            path = RAW / "tstar" / f"tstar{t_star:g}_seed{seed}.txt"
            jobs.append((path, evacuate(path, scheme="hybrid", dt=DT, t_star=t_star, seed=seed, **SECOND_TARGET)))
    for seed in SEEDS:
        path = RAW / "tstar" / f"tsdmd_seed{seed}.txt"
        jobs.append((path, evacuate(path, scheme="tsdmd", dt=DT, seed=seed, **SECOND_TARGET)))
    run_all(jobs)


if __name__ == "__main__":
    main()
