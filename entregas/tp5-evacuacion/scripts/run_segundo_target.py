"""Estudio del segundo target (apéndice) con TSDMD puro, N = AGENTS, semillas 301 a 310: un target común
en (L/2, -D) con D en {1,25; 1,5; 2; 3; 5; 10; 20} m contra "alejarse" (-y debajo de la puerta).

Uso: python scripts/run_segundo_target.py
"""
from common import AGENTS, DT, RAW, evacuate, run_all

DISTANCES = (1.25, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0)
SEEDS = range(301, 311)


def main() -> None:
    jobs = []
    for seed in SEEDS:
        path = RAW / "segundo_target" / f"away_seed{seed}.txt"
        jobs.append((path, evacuate(path, scheme="tsdmd", agents=AGENTS, dt=DT, seed=seed, second_target="away")))
        for d in DISTANCES:
            path = RAW / "segundo_target" / f"point{d:g}_seed{seed}.txt"
            jobs.append((path, evacuate(path, scheme="tsdmd", agents=AGENTS, dt=DT, seed=seed, second_target="point",
                                        second_distance=d)))
    run_all(jobs)


if __name__ == "__main__":
    main()
