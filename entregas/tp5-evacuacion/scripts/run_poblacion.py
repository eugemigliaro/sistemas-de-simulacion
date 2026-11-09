"""Puntos a y b: los tres esquemas con N = AGENTS, las mismas 30 semillas (401 a 430).
Además, una corrida con cuadros por esquema para las animaciones (semilla 401).

Uso: python scripts/run_poblacion.py [esquemas...]   (por omisión, tsdmd, hybrid y edmd)
"""
import sys

from common import AGENTS, CORE_REDUCTION, DT, RAW, SECOND_TARGET, T_STAR, evacuate, run_all

SEEDS = range(401, 431)
# nombre: opciones (edmd_nucleo es EDMD puro con la regla alternativa, decisión 7 del 2026-11-09).
SCHEMES = {"tsdmd": {"scheme": "tsdmd"}, "hybrid": {"scheme": "hybrid", "t_star": T_STAR},
           "edmd": {"scheme": "edmd"}, "edmd_nucleo": {"scheme": "edmd", "core_reduction": CORE_REDUCTION}}
DEFAULT = ("tsdmd", "hybrid", "edmd")


def main() -> None:
    jobs = []
    chosen = sys.argv[1:] or list(DEFAULT)
    for name, extra in ((k, v) for k, v in SCHEMES.items() if k in chosen):
        for seed in SEEDS:
            path = RAW / "poblacion" / f"{name}_seed{seed}.txt"
            jobs.append((path, evacuate(path, agents=AGENTS, dt=DT, seed=seed, **SECOND_TARGET, **extra)))
        path = RAW / "animaciones" / f"{name}_seed401.txt"
        jobs.append((path, evacuate(path, agents=AGENTS, dt=DT, seed=401, output_dt=0.1, **SECOND_TARGET, **extra)))
    run_all(jobs)


if __name__ == "__main__":
    main()
