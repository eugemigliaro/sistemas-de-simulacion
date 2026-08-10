#!/usr/bin/env python3
"""Ejecuta la variación de M con una semilla aleatoria por repetición."""

from __future__ import annotations

import argparse
import csv
import json
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
            fieldnames = fieldnames or reader.fieldnames
            if reader.fieldnames != fieldnames:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--results-root", type=Path)
    parser.add_argument("--repetitions", type=int, default=100)
    arguments = parser.parse_args()

    binary = arguments.binary.resolve()
    config = json.loads(arguments.config.read_text(encoding="utf-8"))
    particle_counts = [config["N_intermediate"], config["N_high"]]
    paths_by_boundary: dict[str, list[Path]] = {}
    for boundary in ("walls", "periodic"):
        for particle_count in particle_counts:
            destination = (
                arguments.output_root.resolve()
                / f"{boundary}-n{particle_count}"
            )
            destination.mkdir(parents=True, exist_ok=True)
            metrics = destination / "metrics-m.csv"
            print(
                f"Midiendo M: boundary={boundary}, N={particle_count}",
                flush=True,
            )
            run(
                [
                    str(binary),
                    "benchmark-random-m",
                    "--N",
                    str(particle_count),
                    "--L",
                    str(config["L"]),
                    "--rc",
                    str(config["rc"]),
                    "--r-min",
                    str(config["r_min"]),
                    "--r-max",
                    str(config["r_max"]),
                    "--boundary",
                    boundary,
                    "--attempts",
                    str(config["attempts_per_particle"]),
                    "--repetitions",
                    str(arguments.repetitions),
                    "--output",
                    str(metrics),
                ]
            )
            paths_by_boundary.setdefault(boundary, []).append(metrics)

    if arguments.results_root is not None:
        for boundary, paths in paths_by_boundary.items():
            combine_metrics(
                paths,
                arguments.results_root.resolve()
                / f"measurements-m-{boundary}.csv",
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
