from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .data import Observation


@dataclass(frozen=True)
class Summary:
    model: str
    density: float
    eta: float
    realizations: int
    stationary_start: float
    polarization_mean: float
    polarization_std: float
    cluster_mean: float
    cluster_std: float
    cim_time_ns_mean: float


def _mean(values: list[float]) -> float:
    if not values:
        raise ValueError("no hay valores para promediar")
    return statistics.fmean(values)


def summarize(
    observations: Iterable[Observation],
    stationary_start: float,
) -> list[Summary]:
    if stationary_start < 0:
        raise ValueError("stationary_start debe ser no negativo")

    by_run: dict[tuple[str, float, float, int], list[Observation]] = defaultdict(list)
    for observation in observations:
        if observation.time >= stationary_start:
            key = (
                observation.model,
                observation.density,
                observation.eta,
                observation.seed,
            )
            by_run[key].append(observation)
    if not by_run:
        raise ValueError("ninguna observación pertenece al estacionario")

    run_means: dict[tuple[str, float, float], list[tuple[float, float, float]]] = (
        defaultdict(list)
    )
    for (model, density, eta, _seed), rows in by_run.items():
        run_means[(model, density, eta)].append(
            (
                _mean([row.polarization for row in rows]),
                _mean([row.largest_cluster_fraction for row in rows]),
                _mean([float(row.cim_time_ns) for row in rows]),
            )
        )

    summaries: list[Summary] = []
    for (model, density, eta), values in sorted(run_means.items()):
        polarizations = [value[0] for value in values]
        clusters = [value[1] for value in values]
        cim_times = [value[2] for value in values]
        summaries.append(
            Summary(
                model=model,
                density=density,
                eta=eta,
                realizations=len(values),
                stationary_start=stationary_start,
                polarization_mean=_mean(polarizations),
                polarization_std=(
                    statistics.stdev(polarizations)
                    if len(polarizations) > 1
                    else 0.0
                ),
                cluster_mean=_mean(clusters),
                cluster_std=(
                    statistics.stdev(clusters)
                    if len(clusters) > 1
                    else 0.0
                ),
                cim_time_ns_mean=_mean(cim_times),
            )
        )
    return summaries


SUMMARY_FIELDS = (
    "model",
    "density",
    "eta",
    "realizations",
    "stationary_start",
    "polarization_mean",
    "polarization_std",
    "cluster_mean",
    "cluster_std",
    "cim_time_ns_mean",
)


def write_summaries(path: str | Path, summaries: Iterable[Summary]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for summary in summaries:
            writer.writerow(
                {
                    "model": summary.model,
                    "density": summary.density,
                    "eta": summary.eta,
                    "realizations": summary.realizations,
                    "stationary_start": summary.stationary_start,
                    "polarization_mean": summary.polarization_mean,
                    "polarization_std": summary.polarization_std,
                    "cluster_mean": summary.cluster_mean,
                    "cluster_std": summary.cluster_std,
                    "cim_time_ns_mean": summary.cim_time_ns_mean,
                }
            )


def read_summaries(path: str | Path) -> list[Summary]:
    source = Path(path)
    result: list[Summary] = []
    with source.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        if tuple(reader.fieldnames or ()) != SUMMARY_FIELDS:
            raise ValueError(f"{source}: encabezado de resumen inesperado")
        for row in reader:
            result.append(
                Summary(
                    model=row["model"],
                    density=float(row["density"]),
                    eta=float(row["eta"]),
                    realizations=int(row["realizations"]),
                    stationary_start=float(row["stationary_start"]),
                    polarization_mean=float(row["polarization_mean"]),
                    polarization_std=float(row["polarization_std"]),
                    cluster_mean=float(row["cluster_mean"]),
                    cluster_std=float(row["cluster_std"]),
                    cim_time_ns_mean=float(row["cim_time_ns_mean"]),
                )
            )
    if not result:
        raise ValueError(f"{source}: resumen vacío")
    return result
