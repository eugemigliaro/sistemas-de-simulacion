"""Corridas de TSDMD puro con N = AGENTS para los atascos (apéndice; decisiones del 2026-11-16):
- animaciones/atasco_seed415.txt: TSDMD con cuadros, la semilla que se traba más temprano con
  N = 60 en los puntos a y b (última salida a los 21 s).
- exploracion/kn1.2e6_seed*.txt: contactos diez veces más rígidos (k = 1,2e6 N/m; dt = 1 ms
  para resolver el choque más rígido), en las semillas de a y b (401 a 450).
- exploracion/kn1.2e6_kt2.4e6_seed*.txt: k y kappa diez veces mayores, para separar la
  rigidez de la fricción (la fricción del SFM, kappa xi dv_t, baja con la superposición).

Uso: python scripts/run_exploracion.py
"""
from common import AGENTS, DT, RAW, SECOND_TARGET, evacuate, run_all

CLOGGING = 415
SEEDS = range(401, 451)
# nombre: parámetros que cambian respecto del paper
VARIANTS = {"kn1.2e6": {"kn": 1.2e6, "dt": 1e-3}, "kn1.2e6_kt2.4e6": {"kn": 1.2e6, "kt": 2.4e6, "dt": 1e-3}}


def main() -> None:
    jobs = []
    path = RAW / "animaciones" / f"atasco_seed{CLOGGING}.txt"
    jobs.append((path, evacuate(path, scheme="tsdmd", agents=AGENTS, dt=DT, seed=CLOGGING, output_dt=0.1,
                                **SECOND_TARGET)))
    for name, options in VARIANTS.items():
        for seed in SEEDS:
            path = RAW / "exploracion" / f"{name}_seed{seed}.txt"
            jobs.append((path, evacuate(path, scheme="tsdmd", agents=AGENTS, seed=seed, **options, **SECOND_TARGET)))
    run_all(jobs)


if __name__ == "__main__":
    main()
