"""Estudio para elegir N (apéndice; decisiones del 2026-11-15): sala de 50 m, N de 20 a 100
de a 10, los tres esquemas (híbrido con relajación analítica y T* = 0,002 s, la configuración
principal cuando se hizo el estudio), semillas 901 a 920.
Medida: costo por segundo simulado, comparado semilla por semilla. Tiempos en esta
computadora, con 4 corridas a la vez (TP5_WORKERS).

Uso: python scripts/run_elegir_n.py
"""
import os

from common import DT, EDMD_OPTIONS, RAW, SECOND_TARGET, evacuate, run_all

COUNTS = range(20, 101, 10)
SEEDS = range(901, 921)
WORKERS = int(os.environ.get("TP5_WORKERS", "4"))
HYBRID = {"t_star": 0.002, "relaxation": "analytic"}


def main() -> None:
    jobs = []
    for n in COUNTS:
        for seed in SEEDS:
            base = dict(agents=n, dt=DT, seed=seed, **SECOND_TARGET)
            for scheme, extra in (("tsdmd", {}), ("hybrid", HYBRID),
                                  ("edmd", EDMD_OPTIONS)):
                path = RAW / "elegir_n" / f"n{n}_{scheme}_seed{seed}.txt"
                jobs.append((path, evacuate(path, scheme=scheme, **base, **extra)))
    run_all(jobs, workers=WORKERS)


if __name__ == "__main__":
    main()
