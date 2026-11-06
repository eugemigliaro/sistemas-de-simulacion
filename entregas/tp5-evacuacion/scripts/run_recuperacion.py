"""Estudio de la recuperación de v_d en EDMD puro, en el sistema chico (N = 60, L = 15 m),
semillas 701 a 710: patadas con varios delta contra relajación analítica con varias
tolerancias de reapuntado, más TSDMD y el híbrido como referencias.

Uso: python scripts/run_recuperacion.py
"""
from common import DT, RAW, SECOND_TARGET, T_STAR, evacuate, run_all

SEEDS = range(701, 711)
SMALL = {"agents": 60, "side": 15.0}
KICKS = (0.01, 0.02, 0.05, 0.1, 0.2)
AIMS = (0.003, 0.01, 0.03, 0.1)


def main() -> None:
    jobs = []
    for seed in SEEDS:
        base = dict(dt=DT, seed=seed, **SMALL, **SECOND_TARGET)
        for kick in KICKS:
            path = RAW / "recuperacion" / f"kicks{kick:g}_seed{seed}.txt"
            jobs.append((path, evacuate(path, scheme="edmd", relaxation="kicks", kick=kick, **base)))
        for aim in AIMS:
            path = RAW / "recuperacion" / f"analytic{aim:g}_seed{seed}.txt"
            jobs.append((path, evacuate(path, scheme="edmd", relaxation="analytic", aim_tolerance=aim, **base)))
        path = RAW / "recuperacion" / f"tsdmd_seed{seed}.txt"
        jobs.append((path, evacuate(path, scheme="tsdmd", **base)))
        path = RAW / "recuperacion" / f"hybrid_seed{seed}.txt"
        jobs.append((path, evacuate(path, scheme="hybrid", t_star=T_STAR, **base)))
    run_all(jobs)


if __name__ == "__main__":
    main()
