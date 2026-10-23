"""Rutas, parámetros de los estudios y ejecución del motor."""
from __future__ import annotations

import csv
import gzip
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python/src"))

ENGINE = ROOT / "cpp/build/release/tp4"
BENCHMARK = ROOT / "cpp/build/release/benchmark"
RAW = ROOT / "experiments/raw"
RESULTS = ROOT / "experiments/results"
FIGURES = ROOT / "presentacion/figuras"
VIDEOS = ROOT / "presentacion/videos"

RADIUS = 0.51
PARTICLE_RADIUS = 0.0175
SEEDS = list(range(1, 11))
# Por encima de esta cantidad el rechazo secuencial no ubica las partículas.
DENSEST_RANDOM_LAYOUT = 430
# Paso elegido con el estudio de energía (2.1.a); ver experiments/results/energy-summary.csv.
DT = 2e-5
COUNTS = [20, 50, 100, 200, 300, 400, 450, 500, 550, 600, 650]
# Densidad (2.4.a): las N de 2.1.b en las que las diez realizaciones llegan a
# Fu = 1 antes de 300 s, más N bajos para ubicar el mínimo de <t90>.
DENSITY_COUNTS = [5, 10, 15, 20, 30, 50, 100, 200, 300]
POSITIONS = [round(PARTICLE_RADIUS + i * (RADIUS - 2 * PARTICLE_RADIUS) / 10, 6) for i in range(11)]
WORKERS = int(os.environ.get("TP4_WORKERS", max(1, (os.cpu_count() or 2) // 2)))


def layout_for(n: int) -> str:
    return "lattice" if n > DENSEST_RANDOM_LAYOUT else "random"


def output_every(interval: float, dt: float) -> int:
    every = round(interval / dt)
    if abs(every * dt - interval) > 1e-9 * interval:
        raise ValueError("el intervalo de salida debe ser múltiplo de dt")
    return every


def _store(partial: Path, final: Path) -> None:
    if final.suffix == ".gz":
        with open(partial, "rb") as source, gzip.open(final, "wb", compresslevel=3) as target:
            shutil.copyfileobj(source, target)
        partial.unlink()
    else:
        partial.rename(final)


def billiard(output: Path, n: int, tf: float, interval: float, seed: int, x0: float | None = None,
             dt: float = DT, compress: bool = True, allow_divergence: bool = False) -> Path:
    """Corre el billar si la salida todavía no existe y devuelve su ruta.

    Escribe en un archivo temporal y lo renombra al terminar, de modo que una
    corrida interrumpida no deja una salida parcial que parezca completa. Con
    allow_divergence, si el motor se detiene porque el paso es demasiado grande
    se conservan los cuadros escritos en un archivo terminado en .diverged.
    """
    final = output.with_suffix(output.suffix + ".gz") if compress else output
    stopped = final.with_name(output.name + ".diverged" + (".gz" if compress else ""))
    if final.exists():
        return final
    if allow_divergence and stopped.exists():
        return stopped
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_suffix(".partial")
    arguments = [str(ENGINE), "billiard", "--n", str(n), "--dt", repr(dt), "--tf", repr(tf),
                 "--output-every", str(output_every(interval, dt)), "--seed", str(seed),
                 "--layout", layout_for(n), "--output", str(partial)]
    if x0 is not None:
        arguments += ["--x0", repr(x0)]
    try:
        subprocess.run(arguments, check=True, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as error:
        if not allow_divergence or "reducir dt" not in error.stderr:
            raise
        _store(partial, stopped)
        return stopped
    _store(partial, final)
    return final


def diverged(path: Path) -> bool:
    return ".diverged" in path.name


def parallel(function, items, workers: int = WORKERS) -> list:
    items = list(items)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(function, items))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="") as stream:
        return list(csv.DictReader(stream))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def require_engine() -> None:
    if not ENGINE.exists():
        raise SystemExit("falta el motor: correr make release")
