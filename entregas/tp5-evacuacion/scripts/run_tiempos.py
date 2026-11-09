"""Puntos c y d: tiempos de ejecución, todos en la misma computadora [TP05, p. 4].

Para correr en la computadora que mide los tiempos, sin otras tareas:
    make release                       # mismo commit para todas las corridas
    python scripts/run_tiempos.py c    # barrido de T* con TSDMD y EDMD de referencia
    python scripts/run_tiempos.py d    # escalamiento con N, en las dos variantes
Siempre con 4 corridas a la vez (TP5_WORKERS cambia ese número: no cambiarlo entre c y d).
Guarda los datos del equipo en experiments/results/maquina.json. El tiempo de cada corrida
es el del bucle de simulación, medido por el motor (`wall_seconds` en el pie de la salida),
sin escribir cuadros.

Punto c: N = AGENTS, semillas 501 a 510; híbrido con cada T* de T_STARS, TSDMD y EDMD.
Punto d: N en {100, 200, 400, 600, 800, 1000}, semillas 601 a 605, a densidad constante
(la del sistema base: L = 50 m sqrt(N/AGENTS)) y a L = 50 m; EDMD puro solo con N <= 600 y
3 semillas. EDMD puro usa la regla de choque elegida (EDMD_OPTIONS).
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys

from common import AGENTS, DT, EDMD_OPTIONS, RAW, RESULTS, SECOND_TARGET, T_STAR, T_STARS, evacuate, run_all

WORKERS = int(os.environ.get("TP5_WORKERS", "4"))
# Carpeta propia del sistema base: las corridas viejas (N = 500) quedan en tiempos/c y tiempos/d.
OUT = RAW / "tiempos" / f"base{AGENTS}"
COUNTS = (100, 200, 400, 600, 800, 1000)


def machine() -> None:
    info = {"platform": platform.platform(), "processor": platform.processor(), "cpu_count": os.cpu_count(),
            "python": platform.python_version(), "workers": WORKERS}
    for command in (["lscpu"], ["sysctl", "-n", "machdep.cpu.brand_string"], ["g++", "--version"],
                    ["git", "rev-parse", "HEAD"]):
        try:
            info[command[0]] = subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "maquina.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))


def point_c() -> list:
    jobs = []
    for seed in range(501, 511):
        base = dict(agents=AGENTS, dt=DT, seed=seed, **SECOND_TARGET)
        for t_star in T_STARS:
            path = OUT / "c" / f"hybrid_tstar{t_star:g}_seed{seed}.txt"
            jobs.append((path, evacuate(path, scheme="hybrid", t_star=t_star, **base)))
        for scheme, extra in (("tsdmd", {}), ("edmd", EDMD_OPTIONS)):
            path = OUT / "c" / f"{scheme}_seed{seed}.txt"
            jobs.append((path, evacuate(path, scheme=scheme, **base, **extra)))
    return jobs


def point_d() -> list:
    jobs = []
    for n in COUNTS:
        for variant, side in (("densidad", 50.0 * (n / AGENTS) ** 0.5), ("sala", 50.0)):
            for seed in range(601, 606):
                base = dict(dt=DT, seed=seed, agents=n, side=round(side, 6), **SECOND_TARGET)
                schemes = {"tsdmd": {}, "hybrid": {"t_star": T_STAR}}
                if n <= 600 and seed <= 603:
                    schemes["edmd"] = EDMD_OPTIONS
                for scheme, extra in schemes.items():
                    path = OUT / "d" / f"{variant}_n{n}_{scheme}_seed{seed}.txt"
                    jobs.append((path, evacuate(path, scheme=scheme, **base, **extra)))
    return jobs


def main() -> None:
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what not in ("c", "d"):
        raise SystemExit("uso: run_tiempos.py c|d")
    machine()
    run_all(point_c() if what == "c" else point_d(), workers=WORKERS)


if __name__ == "__main__":
    main()
