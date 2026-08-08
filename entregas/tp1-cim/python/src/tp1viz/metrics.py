"""Lectura, validación y agregación de mediciones de rendimiento."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean, pstdev


REQUIRED_COLUMNS = (
    "seed",
    "boundary",
    "method",
    "N",
    "L",
    "M",
    "rc",
    "repetition",
    "time_ns",
    "neighbor_pairs",
    "distance_evaluations",
)

SUMMARY_COLUMNS = (
    "seed",
    "boundary",
    "N",
    "L",
    "rc",
    "M",
    "method",
    "samples",
    "mean_time_ns",
    "stddev_time_ns",
    "neighbor_pairs",
    "mean_distance_evaluations",
)


class MetricsError(ValueError):
    """Indica que un archivo de métricas no respeta el contrato esperado."""


@dataclass(frozen=True)
class Metric:
    """Una repetición individual producida por un benchmark."""

    seed: int
    boundary: str
    method: str
    particle_count: int
    side: float
    cells_per_side: int
    cutoff: float
    repetition: int
    time_ns: int
    neighbor_pairs: int
    distance_evaluations: int


@dataclass(frozen=True)
class MetricGroup:
    """Parámetros que deben permanecer iguales entre repeticiones."""

    seed: int
    boundary: str
    particle_count: int
    side: float
    cutoff: float
    cells_per_side: int
    method: str


@dataclass(frozen=True)
class MetricSummary:
    """Estadísticos de repeticiones con iguales parámetros."""

    group: MetricGroup
    samples: int
    mean_time_ns: float
    stddev_time_ns: float
    neighbor_pairs: int
    mean_distance_evaluations: float


def _parse_int(row: dict[str, str], column: str, location: str) -> int:
    try:
        return int(row[column])
    except (TypeError, ValueError) as error:
        raise MetricsError(
            f"{location}: {column} debe ser un número entero"
        ) from error


def _parse_float(row: dict[str, str], column: str, location: str) -> float:
    try:
        return float(row[column])
    except (TypeError, ValueError) as error:
        raise MetricsError(
            f"{location}: {column} debe ser un número real"
        ) from error


def _validate_metric(metric: Metric, location: str) -> None:
    if metric.seed < 0:
        raise MetricsError(f"{location}: seed no puede ser negativo")
    if metric.boundary not in {"walls", "periodic"}:
        raise MetricsError(f"{location}: boundary debe ser walls o periodic")
    if metric.method not in {"brute_force", "cim"}:
        raise MetricsError(f"{location}: method debe ser brute_force o cim")
    if metric.particle_count <= 0:
        raise MetricsError(f"{location}: N debe ser positivo")
    if not math.isfinite(metric.side) or metric.side <= 0:
        raise MetricsError(f"{location}: L debe ser positivo")
    if metric.cells_per_side <= 0:
        raise MetricsError(f"{location}: M debe ser positivo")
    if not math.isfinite(metric.cutoff) or metric.cutoff < 0:
        raise MetricsError(f"{location}: rc no puede ser negativo")
    if metric.repetition <= 0:
        raise MetricsError(f"{location}: repetition debe comenzar en 1")
    if metric.time_ns < 0:
        raise MetricsError(f"{location}: time_ns no puede ser negativo")
    if metric.neighbor_pairs < 0:
        raise MetricsError(f"{location}: neighbor_pairs no puede ser negativo")
    if metric.distance_evaluations < 0:
        raise MetricsError(
            f"{location}: distance_evaluations no puede ser negativo"
        )
    if metric.cells_per_side == 1 and metric.method != "brute_force":
        raise MetricsError(f"{location}: M=1 debe usar brute_force")
    if metric.cells_per_side > 1 and metric.method != "cim":
        raise MetricsError(f"{location}: M>1 debe usar cim")


def _metric_from_row(row: dict[str, str], location: str) -> Metric:
    metric = Metric(
        seed=_parse_int(row, "seed", location),
        boundary=row["boundary"],
        method=row["method"],
        particle_count=_parse_int(row, "N", location),
        side=_parse_float(row, "L", location),
        cells_per_side=_parse_int(row, "M", location),
        cutoff=_parse_float(row, "rc", location),
        repetition=_parse_int(row, "repetition", location),
        time_ns=_parse_int(row, "time_ns", location),
        neighbor_pairs=_parse_int(row, "neighbor_pairs", location),
        distance_evaluations=_parse_int(
            row, "distance_evaluations", location
        ),
    )
    _validate_metric(metric, location)
    return metric


def read_metrics(paths: Sequence[Path]) -> list[Metric]:
    """Lee uno o más CSV y rechaza mediciones ambiguas o duplicadas."""

    if not paths:
        raise MetricsError("se requiere al menos un archivo de métricas")

    metrics: list[Metric] = []
    seen_repetitions: set[tuple[MetricGroup, int]] = set()

    for path in paths:
        try:
            input_file = path.open(newline="", encoding="utf-8")
        except OSError as error:
            raise MetricsError(f"no se pudo leer {path}: {error}") from error

        with input_file:
            reader = csv.DictReader(input_file)
            if reader.fieldnames is None:
                raise MetricsError(f"{path}: el archivo está vacío")

            missing = [
                column
                for column in REQUIRED_COLUMNS
                if column not in reader.fieldnames
            ]
            if missing:
                raise MetricsError(
                    f"{path}: faltan columnas requeridas: {', '.join(missing)}"
                )

            rows_in_file = 0
            for line_number, row in enumerate(reader, start=2):
                if all(value is None or value == "" for value in row.values()):
                    continue
                location = f"{path}:{line_number}"
                if None in row:
                    raise MetricsError(
                        f"{location}: la fila contiene columnas adicionales"
                    )
                metric = _metric_from_row(row, location)
                group = group_for(metric)
                repetition_key = (group, metric.repetition)
                if repetition_key in seen_repetitions:
                    raise MetricsError(
                        f"{location}: repetición {metric.repetition} duplicada "
                        "para el mismo experimento"
                    )
                seen_repetitions.add(repetition_key)
                metrics.append(metric)
                rows_in_file += 1

            if rows_in_file == 0:
                raise MetricsError(f"{path}: no contiene mediciones")

    return metrics


def group_for(metric: Metric) -> MetricGroup:
    """Obtiene la identidad experimental de una medición."""

    return MetricGroup(
        seed=metric.seed,
        boundary=metric.boundary,
        particle_count=metric.particle_count,
        side=metric.side,
        cutoff=metric.cutoff,
        cells_per_side=metric.cells_per_side,
        method=metric.method,
    )


def summarize_metrics(metrics: Sequence[Metric]) -> list[MetricSummary]:
    """Calcula media y desvío poblacional para cada valor de M."""

    grouped: dict[MetricGroup, list[Metric]] = defaultdict(list)
    for metric in metrics:
        grouped[group_for(metric)].append(metric)

    summaries: list[MetricSummary] = []
    for group, repetitions in grouped.items():
        if len(repetitions) < 2:
            raise MetricsError(
                "se necesitan al menos dos repeticiones para calcular el "
                f"desvío: N={group.particle_count}, M={group.cells_per_side}"
            )

        pair_counts = {metric.neighbor_pairs for metric in repetitions}
        if len(pair_counts) != 1:
            raise MetricsError(
                "neighbor_pairs cambió entre repeticiones para "
                f"N={group.particle_count}, M={group.cells_per_side}"
            )

        times = [metric.time_ns for metric in repetitions]
        evaluations = [
            metric.distance_evaluations for metric in repetitions
        ]
        summaries.append(
            MetricSummary(
                group=group,
                samples=len(repetitions),
                mean_time_ns=fmean(times),
                stddev_time_ns=pstdev(times),
                neighbor_pairs=pair_counts.pop(),
                mean_distance_evaluations=fmean(evaluations),
            )
        )

    return sorted(
        summaries,
        key=lambda summary: (
            summary.group.particle_count,
            summary.group.seed,
            summary.group.boundary,
            summary.group.side,
            summary.group.cutoff,
            summary.group.cells_per_side,
        ),
    )


def write_summaries(path: Path, summaries: Sequence[MetricSummary]) -> None:
    """Escribe los estadísticos en un CSV reutilizable."""

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        output_file = path.open("w", newline="", encoding="utf-8")
    except OSError as error:
        raise MetricsError(f"no se pudo escribir {path}: {error}") from error

    with output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=SUMMARY_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for summary in summaries:
            group = summary.group
            writer.writerow(
                {
                    "seed": group.seed,
                    "boundary": group.boundary,
                    "N": group.particle_count,
                    "L": format(group.side, ".17g"),
                    "rc": format(group.cutoff, ".17g"),
                    "M": group.cells_per_side,
                    "method": group.method,
                    "samples": summary.samples,
                    "mean_time_ns": format(summary.mean_time_ns, ".6f"),
                    "stddev_time_ns": format(
                        summary.stddev_time_ns, ".6f"
                    ),
                    "neighbor_pairs": summary.neighbor_pairs,
                    "mean_distance_evaluations": format(
                        summary.mean_distance_evaluations, ".6f"
                    ),
                }
            )
