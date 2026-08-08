#!/usr/bin/env python3
"""Genera y mide los estudios de N con densidad libre y fija."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ejecuta los experimentos de variación de N del TP1."
    )
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
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

    for boundary in config["boundaries"]:
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
                static_path = destination / "static.txt"
                dynamic_path = destination / "dynamic.txt"
                metrics_path = destination / "metrics.csv"
                print(
                    f"Generando {boundary}/{regime}: N={particle_count}, "
                    f"L={side:.8g}, M={cells_per_side}",
                    flush=True,
                )
                run(
                    [
                        str(binary),
                        "generate",
                        "--N",
                        str(particle_count),
                        "--L",
                        format(side, ".17g"),
                        "--r-min",
                        str(config["r_min"]),
                        "--r-max",
                        str(config["r_max"]),
                        "--seed",
                        str(config["seed"]),
                        "--boundary",
                        boundary,
                        "--attempts",
                        str(config["attempts_per_particle"]),
                        "--static",
                        str(static_path),
                        "--dynamic",
                        str(dynamic_path),
                    ]
                )
                run(
                    [
                        str(binary),
                        "benchmark-n",
                        "--M",
                        str(cells_per_side),
                        "--static",
                        str(static_path),
                        "--dynamic",
                        str(dynamic_path),
                        "--rc",
                        str(config["rc"]),
                        "--boundary",
                        boundary,
                        "--seed",
                        str(config["seed"]),
                        "--repetitions",
                        str(config["repetitions"]),
                        "--output",
                        str(metrics_path),
                    ]
                )

    print(f"Experimentos escritos en {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
