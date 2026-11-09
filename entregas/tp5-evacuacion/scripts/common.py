"""Utilidades compartidas por los scripts de corridas: el motor, las carpetas y un
ejecutor en paralelo que saltea las salidas ya completas (las corridas se pueden
interrumpir y relanzar)."""
from __future__ import annotations

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "cpp" / "build" / "release" / "tp5"
RAW = ROOT / "experiments" / "raw"
RESULTS = ROOT / "experiments" / "results"
FIGURES = ROOT / "presentacion" / "figuras"
VIDEOS = ROOT / "presentacion" / "videos"
sys.path.insert(0, str(ROOT / "python" / "src"))

WORKERS = int(os.environ.get("TP5_WORKERS", "7"))

# N = 200 en todo el TP salvo el estudio del dt (consulta del 06/11; la consigna dice 500).
AGENTS = 200

# Elegidos con los estudios (se actualizan al tenerlos; ver docs/decisiones.md).
DT = 2e-3            # test del dt (run_dt.py): J no difiere del de 0,5 ms; ver experiments/results/dt.csv
SECOND_TARGET = {"second_target": "away"}  # estudio del segundo target (run_segundo_target.py)
T_STAR = 0.01        # benchmark de T* con N = 200 (bench_tstar.py): menor mínimo; ver docs/decisiones.md
T_STARS = (0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0)
CORE_REDUCTION = 0.0106  # m, compresión media en el tapón de TSDMD con N = 200 (medir_compresion.py)
EDMD_OPTIONS: dict = {}  # regla de choque de EDMD puro (decisiones 6 y 7 del 2026-11-09)


def complete(path: Path) -> bool:
    """La salida terminó si tiene el pie con el resumen."""
    if not path.exists():
        return False
    with open(path, "rb") as fh:
        fh.seek(max(0, path.stat().st_size - 600))
        return b"# exited" in fh.read()


def evacuate(path: Path, **options) -> list[str]:
    """Línea de comandos de `tp5 evacuate` con las opciones dadas (guiones bajos -> guiones)."""
    command = [str(ENGINE), "evacuate"]
    for key, value in options.items():
        command += [f"--{key.replace('_', '-')}", f"{value:g}" if isinstance(value, float) else str(value)]
    return command + ["--output", str(path)]


def run_all(jobs: list[tuple[Path, list[str]]], workers: int = WORKERS) -> None:
    """Corre (salida, comando) en paralelo; imprime el resumen de stderr de cada uno."""
    pending = [(path, command) for path, command in jobs if not complete(path)]
    print(f"{len(jobs)} corridas, {len(jobs) - len(pending)} ya hechas, {len(pending)} por correr "
          f"({workers} en paralelo)", flush=True)

    def one(job):
        path, command = job
        path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(command, capture_output=True, text=True)
        return f"{path.relative_to(RAW)}: {result.stderr.strip().splitlines()[-1] if result.stderr else result.returncode}"

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for line in pool.map(one, pending):
            print(line, flush=True)
