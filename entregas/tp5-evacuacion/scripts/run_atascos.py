"""Fluctuación en contacto y atascos (apéndice): TSDMD puro con N = AGENTS, las semillas de
los puntos a y b (401 a 430) sin fluctuación y con fluctuación de 5, 10 y 20 % de m v_d/tau
(comparación pareada: mismas condiciones iniciales). Corte por atasco: 300 s sin salidas.

Uso: python scripts/run_atascos.py
"""
from common import AGENTS, DT, RAW, SECOND_TARGET, evacuate, run_all

SEEDS = range(401, 431)
NOISES = (0.0, 0.05, 0.1, 0.2)


def main() -> None:
    jobs = []
    for noise in NOISES:
        for seed in SEEDS:
            path = RAW / "atascos" / f"noise{noise:g}_seed{seed}.txt"
            jobs.append((path, evacuate(path, scheme="tsdmd", agents=AGENTS, dt=DT, seed=seed, noise=noise,
                                        **SECOND_TARGET)))
    run_all(jobs)


if __name__ == "__main__":
    main()
