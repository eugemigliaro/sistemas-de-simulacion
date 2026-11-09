"""Corridas sueltas con N = AGENTS para los atascos:
- animaciones/atasco_seed405.txt: TSDMD con cuadros, una semilla que se traba temprano.
- exploracion/kn1.2e6_seed*.txt: prueba de la hipótesis de la compresión, TSDMD con k diez
  veces mayor (menos compresión; dt = 1 ms para resolver el choque más rígido) en tres semillas
  que con el k del paper evacúan completas (401, 403 y 404).

Uso: python scripts/run_exploracion.py
"""
from common import AGENTS, DT, RAW, SECOND_TARGET, evacuate, run_all

STIFF = {"kn": 1.2e6, "dt": 1e-3}
FINISHING = (401, 403, 404)


def main() -> None:
    jobs = []
    path = RAW / "animaciones" / "atasco_seed405.txt"
    jobs.append((path, evacuate(path, scheme="tsdmd", agents=AGENTS, dt=DT, seed=405, output_dt=0.1, **SECOND_TARGET)))
    for seed in FINISHING:
        path = RAW / "exploracion" / f"kn1.2e6_seed{seed}.txt"
        jobs.append((path, evacuate(path, scheme="tsdmd", agents=AGENTS, seed=seed, **STIFF, **SECOND_TARGET)))
    run_all(jobs)


if __name__ == "__main__":
    main()
