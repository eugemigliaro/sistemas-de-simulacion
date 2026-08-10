#!/usr/bin/env python3
"""Genera y mide los estudios de N con densidad libre y fija."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
from pathlib import Path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def combine_metrics(paths: list[Path], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] | None = None
    rows: list[dict[str, str]] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as input_file:
            reader = csv.DictReader(input_file)
            if reader.fieldnames is None:
                raise SystemExit(f"archivo de métricas vacío: {path}")
            if fieldnames is None:
                fieldnames = reader.fieldnames
            elif reader.fieldnames != fieldnames:
                raise SystemExit(f"columnas incompatibles en {path}")
            rows.extend(reader)
    if fieldnames is None:
        raise SystemExit("no hay métricas para combinar")
    with output.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(
            output_file, fieldnames=fieldnames, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ejecuta los experimentos de variación de N del TP1."
    )
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--results-root", type=Path)
    parser.add_argument(
        "--boundaries",
        nargs="+",
        choices=("walls", "periodic"),
        help="contornos a ejecutar; por defecto usa la configuración",
    )
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    binary = arguments.binary.resolve()
    if not binary.is_file():
        raise SystemExit(f"no existe el ejecutable {binary}")
    try:
        config = json.loads(arguments.config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"no se pudo leer la configuración: {error}") from error

    particle_counts = config["N_values"]
    if len(particle_counts) < 10 or any(value <= 0 for value in particle_counts):
        raise SystemExit("N_values debe contener al menos diez enteros positivos")
    reference_cell_side = config["reference_side"] / config["reference_M"]
    output_root = arguments.output_root.resolve()
    result_paths: dict[tuple[str, str], list[Path]] = {}

    boundaries = arguments.boundaries or config["boundaries"]
    for boundary in boundaries:
        if boundary not in {"walls", "periodic"}:
            raise SystemExit(f"contorno inválido: {boundary}")
        for regime in ("free", "fixed"):
            for particle_count in particle_counts:
                if regime == "free":
                    side = config["free_side"]
                    cells_per_side = config["reference_M"]
                else:
                    side = math.sqrt(
                        particle_count / config["fixed_density"]
                    )
                    cells_per_side = max(
                        1, math.floor(side / reference_cell_side)
                    )

                destination = (
                    output_root / boundary / regime / f"n-{particle_count}"
                )
                destination.mkdir(parents=True, exist_ok=True)
                metrics_path = destination / "metrics.csv"
                print(
                    f"Generando {boundary}/{regime}: N={particle_count}, "
                    f"L={side:.8g}, M={cells_per_side}",
                    flush=True,
                )
                run(
                    [
                        str(binary),
                        "benchmark-random-n",
                        "--N",
                        str(particle_count),
                        "--L",
                        format(side, ".17g"),
                        "--r-min",
                        str(config["r_min"]),
                        "--r-max",
                        str(config["r_max"]),
                        "--boundary",
                        boundary,
                        "--attempts",
                        str(config["attempts_per_particle"]),
                        "--M",
                        str(cells_per_side),
                        "--rc",
                        str(config["rc"]),
                        "--repetitions",
                        str(config["repetitions"]),
                        "--output",
                        str(metrics_path),
                    ]
                )
                result_paths.setdefault((boundary, regime), []).append(
                    metrics_path
                )

    if arguments.results_root is not None:
        results_root = arguments.results_root.resolve()
        for (boundary, regime), paths in result_paths.items():
            combine_metrics(
                paths,
                results_root / f"measurements-n-{boundary}-{regime}.csv",
            )

    print(f"Experimentos escritos en {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
