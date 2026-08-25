from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .data import Observation


@dataclass(frozen=True)
class CimSummary:
    model: str
    density: float
    particle_count: int
    side: float
    cells_per_side: int
    cutoff: float
    samples: int
    seed_count: int
    mean_time_ns: float
    stddev_time_ns: float
    mean_distance_evaluations: float


CIM_FIELDS = (
    "model", "density", "particle_count", "side", "cells_per_side",
    "cutoff", "samples", "seed_count", "mean_time_ns",
    "stddev_time_ns", "mean_distance_evaluations",
)


def summarize_cim(
    observations: Iterable[Observation],
    start: float = 0.0,
) -> list[CimSummary]:
    if start < 0:
        raise ValueError("start debe ser no negativo")
    grouped: dict[tuple, list[Observation]] = defaultdict(list)
    for row in observations:
        if row.time >= start:
            key = (
                row.model,
                row.density,
                row.particle_count,
                row.side,
                row.cells_per_side,
                row.cutoff,
            )
            grouped[key].append(row)
    if not grouped:
        raise ValueError("no hay mediciones CIM en el intervalo")

    result: list[CimSummary] = []
    for key, rows in sorted(grouped.items()):
        times = [float(row.cim_time_ns) for row in rows]
        result.append(
            CimSummary(
                model=key[0],
                density=key[1],
                particle_count=key[2],
                side=key[3],
                cells_per_side=key[4],
                cutoff=key[5],
                samples=len(rows),
                seed_count=len({row.seed for row in rows}),
                mean_time_ns=statistics.fmean(times),
                stddev_time_ns=(statistics.stdev(times) if len(times) > 1 else 0.0),
                mean_distance_evaluations=statistics.fmean(
                    float(row.distance_evaluations) for row in rows
                ),
            )
        )
    return result


def write_cim_summaries(path: str | Path, rows: Iterable[CimSummary]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=CIM_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def read_cim_summaries(path: str | Path) -> list[CimSummary]:
    source = Path(path)
    result: list[CimSummary] = []
    with source.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        if tuple(reader.fieldnames or ()) != CIM_FIELDS:
            raise ValueError(f"{source}: encabezado CIM inesperado")
        for row in reader:
            result.append(
                CimSummary(
                    model=row["model"],
                    density=float(row["density"]),
                    particle_count=int(row["particle_count"]),
                    side=float(row["side"]),
                    cells_per_side=int(row["cells_per_side"]),
                    cutoff=float(row["cutoff"]),
                    samples=int(row["samples"]),
                    seed_count=int(row["seed_count"]),
                    mean_time_ns=float(row["mean_time_ns"]),
                    stddev_time_ns=float(row["stddev_time_ns"]),
                    mean_distance_evaluations=float(
                        row["mean_distance_evaluations"]
                    ),
                )
            )
    if not result:
        raise ValueError(f"{source}: resumen CIM vacío")
    return result


_TP1_LABELS = {
    "fixed": r"TP1, densidad constante ($\rho=1{,}25$)",
    "free": r"TP1, caja constante ($L=20$)",
}


def read_tp1_cim(path: str | Path) -> dict[str, list[tuple[int, float, float]]]:
    source = Path(path)
    grouped: dict[str, list[tuple[int, float, float]]] = defaultdict(list)
    with source.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        fields = set(reader.fieldnames or ())
        required = {"boundary", "N", "method", "mean_time_ns", "stddev_time_ns"}
        if not required <= fields:
            raise ValueError(f"{source}: resumen de TP1 incompatible")
        for row in reader:
            if row["boundary"] != "periodic" or row["method"] != "cim":
                continue
            regime = row.get("regime") or "barrido M"
            grouped[f"{_TP1_LABELS.get(regime, regime)}"].append(
                (
                    int(row["N"]),
                    float(row["mean_time_ns"]),
                    float(row["stddev_time_ns"]),
                )
            )
    if not grouped:
        raise ValueError(f"{source}: no contiene mediciones CIM periódicas")
    return grouped


def plot_cim_comparison(
    tp2_rows: Iterable[CimSummary],
    tp1_path: str | Path,
    output: str | Path,
) -> None:
    rows = list(tp2_rows)
    if not rows:
        raise ValueError("no hay resúmenes CIM del TP2")
    tp1 = read_tp1_cim(tp1_path)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(8, 5))
    for label, values in sorted(tp1.items()):
        values.sort(key=lambda value: value[0])
        axis.errorbar(
            [value[0] for value in values],
            [value[1] / 1000.0 for value in values],
            yerr=[value[2] / 1000.0 for value in values],
            marker="x",
            linestyle="--",
            capsize=3,
            label=label,
        )
    by_model: dict[str, list[CimSummary]] = defaultdict(list)
    for row in rows:
        by_model[row.model].append(row)
    for model, values in sorted(by_model.items()):
        values.sort(key=lambda value: value.particle_count)
        axis.errorbar(
            [value.particle_count for value in values],
            [value.mean_time_ns / 1000.0 for value in values],
            yerr=[value.stddev_time_ns / 1000.0 for value in values],
            marker="o",
            capsize=3,
            label=(
                f"TP2 {'Vicsek' if model == 'vicsek' else 'Votante'}"
                r" ($L=10$)"
            ),
        )
    axis.set_xlabel(r"Cantidad de partículas $N$")
    axis.set_ylabel(r"Tiempo de búsqueda de vecinos [$\mu$s]")
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.grid(alpha=0.25, which="both")
    axis.legend()
    figure.tight_layout()
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180)
    plt.close(figure)
