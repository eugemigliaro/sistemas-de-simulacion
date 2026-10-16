#!/usr/bin/env python3
"""Grafica el resumen del punto 1.1 con barras de desvío estándar."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grafica tiempo medio frente a N.")
    parser.add_argument("summary", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    with arguments.summary.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise ValueError(f"{arguments.summary} no contiene mediciones")
    if any(int(row["repetitions"]) < 10 for row in rows):
        raise ValueError("cada N debe tener al menos diez realizaciones")

    rows.sort(key=lambda row: int(row["particle_count"]))
    particles = [int(row["particle_count"]) for row in rows]
    means = [float(row["runtime_mean_s"]) for row in rows]
    deviations = [float(row["runtime_std_s"]) for row in rows]

    figure, axes = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
    axes.errorbar(
        particles,
        means,
        yerr=deviations,
        fmt="o-",
        capsize=4,
        color="#0066A1",
        ecolor="#D36B2D",
        linewidth=1.8,
        markersize=5,
        label="Media ± desvío estándar",
    )
    axes.set_xscale("log")
    axes.set_yscale("log")
    axes.set_xlabel("Número de partículas, N")
    axes.set_ylabel("Tiempo de ejecución promedio (s)")
    axes.grid(True, which="both", alpha=0.25)
    axes.legend(frameon=False)
    axes.set_title("Rendimiento del motor dirigido por eventos")

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(arguments.output, dpi=180)
    plt.close(figure)
    print(f"Figura escrita en {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
