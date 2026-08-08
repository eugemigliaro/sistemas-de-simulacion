#!/usr/bin/env python3
"""Genera, resuelve y visualiza un caso parametrizable del TP1."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, environment: dict[str, str] | None = None) -> None:
    subprocess.run(command, check=True, env=environment)


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
    parser.add_argument("--N", type=int, default=100)
    parser.add_argument("--L", type=float, default=20.0)
    parser.add_argument("--M", type=int, default=13)
    parser.add_argument("--rc", type=float, default=1.0)
    parser.add_argument("--r-min", type=float, default=0.23)
    parser.add_argument("--r-max", type=float, default=0.26)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--boundary", choices=("walls", "periodic"), default="walls"
    )
    parser.add_argument(
        "--particle",
        default="auto",
        help="ID a destacar o auto para elegir la de mayor grado",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("experiments/raw/demo")
    )
    parser.add_argument(
        "--binary",
        type=Path,
        default=PROJECT_ROOT / "cpp/build/release/tp1",
    )
    parser.add_argument("--open", action="store_true", dest="open_figure")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    binary = arguments.binary.resolve()
    if not binary.is_file():
        raise SystemExit(
            f"no existe {binary}; ejecutar make release antes de la demo"
        )
    if arguments.N <= 0 or arguments.L <= 0 or arguments.M <= 0:
        raise SystemExit("N, L y M deben ser positivos")

    output = arguments.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    static_path = output / "static.txt"
    dynamic_path = output / "dynamic.txt"
    neighbors_path = output / "neighbors.txt"
    figure_path = output / "neighbors.png"

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
            str(arguments.seed),
            "--boundary",
            arguments.boundary,
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
        ]
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
    print(f"Figura: {figure_path}")
    if arguments.open_figure:
        if sys.platform != "darwin":
            raise SystemExit("--open está disponible únicamente en macOS")
        run(["open", str(figure_path)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
