#!/usr/bin/env python3
"""Genera, resuelve y visualiza un caso parametrizable del TP1."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path
from statistics import fmean, pstdev


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(
    command: list[str],
    *,
    environment: dict[str, str] | None = None,
    quiet: bool = False,
) -> None:
    subprocess.run(
        command,
        check=True,
        env=environment,
        stdout=subprocess.DEVNULL if quiet else None,
    )


def timing_summary(
    path: Path, expected_repetitions: int
) -> tuple[float, float, int]:
    try:
        with path.open(newline="", encoding="utf-8") as metrics_file:
            rows = list(csv.DictReader(metrics_file))
        times = [int(row["time_ns"]) for row in rows]
        seeds = [int(row["seed"]) for row in rows]
    except (OSError, KeyError, ValueError) as error:
        raise SystemExit(f"no se pudieron resumir las mediciones: {error}") from error
    if len(times) != expected_repetitions:
        raise SystemExit(
            f"se esperaban {expected_repetitions} mediciones y se leyeron "
            f"{len(times)}"
        )
    if len(set(seeds)) != expected_repetitions:
        raise SystemExit("cada repetición debe tener una semilla diferente")
    return fmean(times), pstdev(times), seeds[0]


def selected_particle(path: Path, requested: str, particle_count: int) -> int:
    if requested != "auto":
        try:
            selected = int(requested)
        except ValueError as error:
            raise SystemExit("particle debe ser auto o un ID entero") from error
        if selected <= 0 or selected > particle_count:
            raise SystemExit(f"particle debe estar entre 1 y {particle_count}")
        return selected

    rows = path.read_text(encoding="utf-8").splitlines()
    return max(
        range(1, particle_count + 1),
        key=lambda particle_id: len(rows[particle_id - 1].split(",")) - 1,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Genera partículas, ejecuta el CIM y crea una figura de vecinos."
        )
    )
    parser.add_argument(
        "--N", type=int, default=100, help="cantidad de partículas (100)"
    )
    parser.add_argument(
        "--L", type=float, default=20.0, help="lado del dominio (20)"
    )
    parser.add_argument(
        "--M", type=int, default=13, help="celdas por lado (13)"
    )
    parser.add_argument(
        "--rc", type=float, default=1.0, help="radio de interacción (1)"
    )
    parser.add_argument(
        "--r-min", type=float, default=0.23, help="radio mínimo (0.23)"
    )
    parser.add_argument(
        "--r-max", type=float, default=0.26, help="radio máximo (0.26)"
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=100_000,
        help="intentos máximos por partícula (100000)",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=100,
        help="sistemas aleatorios independientes a medir (100)",
    )
    parser.add_argument(
        "--boundary",
        choices=("walls", "periodic"),
        default="walls",
        help="paredes o contorno periódico (walls)",
    )
    parser.add_argument(
        "--particle",
        default="auto",
        help="ID para el PNG o auto; el modo interactivo usa clic",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/raw/demo"),
        help="carpeta para archivos y PNG",
    )
    parser.add_argument(
        "--binary",
        type=Path,
        default=PROJECT_ROOT / "cpp/build/release/tp1",
        help="ruta al ejecutable C++ release",
    )
    display = parser.add_mutually_exclusive_group()
    display.add_argument("--open", action="store_true", dest="open_figure")
    display.add_argument(
        "--interactive",
        action="store_true",
        help="abre Matplotlib y permite seleccionar partículas con clic",
    )
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    binary = arguments.binary.resolve()
    if not binary.is_file():
        raise SystemExit(
            f"no existe {binary}; ejecutar make release antes de la demo"
        )
    if (
        arguments.N <= 0
        or arguments.L <= 0
        or arguments.M <= 0
        or arguments.attempts <= 0
        or arguments.repetitions <= 0
    ):
        raise SystemExit(
            "N, L, M, attempts y repetitions deben ser positivos"
        )

    output = arguments.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    static_path = output / "static.txt"
    dynamic_path = output / "dynamic.txt"
    neighbors_path = output / "neighbors.txt"
    metrics_path = output / "metrics.csv"
    figure_path = output / "neighbors.png"

    run(
        [
            str(binary),
            "benchmark-random-n",
            "--N",
            str(arguments.N),
            "--L",
            str(arguments.L),
            "--r-min",
            str(arguments.r_min),
            "--r-max",
            str(arguments.r_max),
            "--boundary",
            arguments.boundary,
            "--attempts",
            str(arguments.attempts),
            "--M",
            str(arguments.M),
            "--rc",
            str(arguments.rc),
            "--repetitions",
            str(arguments.repetitions),
            "--output",
            str(metrics_path),
        ],
        quiet=True,
    )
    mean_time_ns, stddev_time_ns, display_seed = timing_summary(
        metrics_path, arguments.repetitions
    )
    run(
        [
            str(binary),
            "generate",
            "--N",
            str(arguments.N),
            "--L",
            str(arguments.L),
            "--r-min",
            str(arguments.r_min),
            "--r-max",
            str(arguments.r_max),
            "--seed",
            str(display_seed),
            "--boundary",
            arguments.boundary,
            "--attempts",
            str(arguments.attempts),
            "--static",
            str(static_path),
            "--dynamic",
            str(dynamic_path),
        ]
    )
    run(
        [
            str(binary),
            "neighbors",
            "--method",
            "cim",
            "--M",
            str(arguments.M),
            "--static",
            str(static_path),
            "--dynamic",
            str(dynamic_path),
            "--rc",
            str(arguments.rc),
            "--boundary",
            arguments.boundary,
            "--output",
            str(neighbors_path),
        ],
        quiet=True,
    )
    particle_id = selected_particle(
        neighbors_path, arguments.particle, arguments.N
    )

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "python/src")
    environment["MPLCONFIGDIR"] = str(PROJECT_ROOT / "python/.matplotlib")
    environment["XDG_CACHE_HOME"] = str(PROJECT_ROOT / "python/.cache")
    python = PROJECT_ROOT / "python/.venv/bin/python"
    if not python.is_file():
        python = Path(sys.executable)
    run(
        [
            str(python),
            "-m",
            "tp1viz",
            "plot-neighbors",
            "--static",
            str(static_path),
            "--dynamic",
            str(dynamic_path),
            "--neighbors",
            str(neighbors_path),
            "--particle",
            str(particle_id),
            "--rc",
            str(arguments.rc),
            "--boundary",
            arguments.boundary,
            "--figure",
            str(figure_path),
        ],
        environment=environment,
    )

    print(f"Partícula destacada: {particle_id}")
    print(f"Semilla del sistema mostrado: {display_seed}")
    print(f"Figura: {figure_path}")
    print(
        "Tiempo medio de búsqueda del sistema completo: "
        f"{mean_time_ns / 1_000:.3f} us +/- "
        f"{stddev_time_ns / 1_000:.3f} us "
        f"({arguments.repetitions} repeticiones)."
    )
    if arguments.open_figure:
        if sys.platform != "darwin":
            raise SystemExit("--open está disponible únicamente en macOS")
        run(["open", str(figure_path)])
    elif arguments.interactive:
        run(
            [
                str(python),
                "-m",
                "tp1viz",
                "explore-neighbors",
                "--static",
                str(static_path),
                "--dynamic",
                str(dynamic_path),
                "--neighbors",
                str(neighbors_path),
                "--rc",
                str(arguments.rc),
                "--boundary",
                arguments.boundary,
            ],
            environment=environment,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
