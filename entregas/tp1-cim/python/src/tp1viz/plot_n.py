"""Análisis y figura del tiempo de búsqueda en función de N."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean

from tp1viz.metrics import MetricSummary, MetricsError


N_SUMMARY_COLUMNS = (
    "regime",
    "seed",
    "boundary",
    "N",
    "L",
    "density",
    "rc",
    "M",
    "method",
    "samples",
    "mean_time_ns",
    "stddev_time_ns",
    "neighbor_pairs",
    "mean_distance_evaluations",
)


@dataclass(frozen=True)
class NPoint:
    regime: str
    summary: MetricSummary

    @property
    def density(self) -> float:
        group = self.summary.group
        return group.particle_count / (group.side * group.side)


@dataclass(frozen=True)
class SeriesKey:
    regime: str
    seed: int
    boundary: str
    cutoff: float


def build_n_points(
    free_summaries: Sequence[MetricSummary],
    fixed_summaries: Sequence[MetricSummary],
) -> list[NPoint]:
    """Combina los dos regímenes y valida una medición por valor de N."""

    points = [
        *(NPoint("free", summary) for summary in free_summaries),
        *(NPoint("fixed", summary) for summary in fixed_summaries),
    ]
    seen: set[tuple[SeriesKey, int]] = set()
    for point in points:
        group = point.summary.group
        key = SeriesKey(
            regime=point.regime,
            seed=group.seed,
            boundary=group.boundary,
            cutoff=group.cutoff,
        )
        identity = (key, group.particle_count)
        if identity in seen:
            raise MetricsError(
                "hay más de una medición para "
                f"regime={point.regime}, boundary={group.boundary}, "
                f"N={group.particle_count}"
            )
        seen.add(identity)

    series = _group_series(points)
    for key, values in series.items():
        if len(values) < 2:
            raise MetricsError(
                f"se necesitan al menos dos N para {key.regime}, {key.boundary}"
            )
        if key.regime == "free":
            sides = {point.summary.group.side for point in values}
            if len(sides) != 1:
                raise MetricsError("densidad libre debe mantener L constante")
        else:
            densities = [point.density for point in values]
            reference = densities[0]
            if any(
                not math.isclose(density, reference, rel_tol=1e-9)
                for density in densities[1:]
            ):
                raise MetricsError(
                    "densidad fija debe mantener N/L^2 constante"
                )
    return sorted(
        points,
        key=lambda point: (
            point.summary.group.boundary,
            point.regime,
            point.summary.group.particle_count,
        ),
    )


def _group_series(points: Sequence[NPoint]) -> dict[SeriesKey, list[NPoint]]:
    series: dict[SeriesKey, list[NPoint]] = defaultdict(list)
    for point in points:
        group = point.summary.group
        series[
            SeriesKey(
                regime=point.regime,
                seed=group.seed,
                boundary=group.boundary,
                cutoff=group.cutoff,
            )
        ].append(point)
    return series


def power_law_exponent(
    points: Sequence[NPoint], *, minimum_n: int = 100
) -> float:
    """Ajusta log(t)=alpha*log(N)+b para los puntos asintóticos."""

    selected = [
        point
        for point in points
        if point.summary.group.particle_count >= minimum_n
        and point.summary.mean_time_ns > 0
    ]
    if len(selected) < 2:
        raise MetricsError("faltan puntos positivos para ajustar el exponente")
    x_values = [
        math.log(point.summary.group.particle_count) for point in selected
    ]
    y_values = [math.log(point.summary.mean_time_ns) for point in selected]
    x_mean = fmean(x_values)
    y_mean = fmean(y_values)
    denominator = sum((value - x_mean) ** 2 for value in x_values)
    if denominator == 0:
        raise MetricsError("los valores de N no permiten ajustar el exponente")
    return sum(
        (x_value - x_mean) * (y_value - y_mean)
        for x_value, y_value in zip(x_values, y_values, strict=True)
    ) / denominator


def write_n_summaries(path: Path, points: Sequence[NPoint]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        output_file = path.open("w", newline="", encoding="utf-8")
    except OSError as error:
        raise MetricsError(f"no se pudo escribir {path}: {error}") from error

    with output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=N_SUMMARY_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for point in points:
            summary = point.summary
            group = summary.group
            writer.writerow(
                {
                    "regime": point.regime,
                    "seed": group.seed,
                    "boundary": group.boundary,
                    "N": group.particle_count,
                    "L": format(group.side, ".17g"),
                    "density": format(point.density, ".17g"),
                    "rc": format(group.cutoff, ".17g"),
                    "M": group.cells_per_side,
                    "method": group.method,
                    "samples": summary.samples,
                    "mean_time_ns": format(summary.mean_time_ns, ".6f"),
                    "stddev_time_ns": format(summary.stddev_time_ns, ".6f"),
                    "neighbor_pairs": summary.neighbor_pairs,
                    "mean_distance_evaluations": format(
                        summary.mean_distance_evaluations, ".6f"
                    ),
                }
            )


def plot_n(
    points: Sequence[NPoint],
    output: Path,
    *,
    log_x: bool = False,
    log_y: bool = False,
) -> dict[SeriesKey, float]:
    """Superpone densidad libre y fija con barras de un desvío."""

    if not points:
        raise MetricsError("no hay resúmenes para graficar")
    if log_y and any(point.summary.mean_time_ns <= 0 for point in points):
        raise MetricsError(
            "la escala logarítmica vertical requiere tiempos medios positivos"
        )

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as error:
        raise MetricsError(
            "Matplotlib no está instalado; ejecutar "
            "pip install -r python/requirements.txt"
        ) from error

    series = _group_series(points)
    exponents: dict[SeriesKey, float] = {}
    figure, axes = plt.subplots(figsize=(8, 5))
    for key in sorted(
        series,
        key=lambda item: (item.boundary, item.regime, item.seed),
    ):
        values = sorted(
            series[key], key=lambda point: point.summary.group.particle_count
        )
        exponent = power_law_exponent(values)
        exponents[key] = exponent
        particle_counts = [
            point.summary.group.particle_count for point in values
        ]
        means_us = [point.summary.mean_time_ns / 1_000 for point in values]
        deviations_us = [
            point.summary.stddev_time_ns / 1_000 for point in values
        ]
        regime_label = (
            "Densidad libre" if key.regime == "free" else "Densidad fija"
        )
        boundary_label = (
            "paredes" if key.boundary == "walls" else "periódico"
        )
        axes.errorbar(
            particle_counts,
            means_us,
            yerr=deviations_us,
            marker="o" if key.regime == "free" else "s",
            linestyle="-",
            capsize=3,
            label=(
                f"{regime_label}, {boundary_label}, "
                f"alpha={exponent:.2f}"
            ),
        )

    axes.set_xlabel("N (cantidad de partículas)")
    axes.set_ylabel("Tiempo de búsqueda (µs)")
    axes.grid(True, which="both", alpha=0.3)
    axes.legend()
    if log_x:
        axes.set_xscale("log")
    if log_y:
        axes.set_yscale("log")
    figure.tight_layout()

    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        figure.savefig(output, dpi=160)
    except (OSError, ValueError) as error:
        raise MetricsError(f"no se pudo escribir {output}: {error}") from error
    finally:
        plt.close(figure)
    return exponents
