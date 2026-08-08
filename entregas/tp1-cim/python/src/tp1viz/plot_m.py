"""Figura del tiempo de búsqueda en función de M."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tp1viz.metrics import MetricSummary, MetricsError


@dataclass(frozen=True)
class SeriesKey:
    """Parámetros que identifican una curva completa del barrido de M."""

    seed: int
    boundary: str
    particle_count: int
    side: float
    cutoff: float


def _series_key(summary: MetricSummary) -> SeriesKey:
    group = summary.group
    return SeriesKey(
        seed=group.seed,
        boundary=group.boundary,
        particle_count=group.particle_count,
        side=group.side,
        cutoff=group.cutoff,
    )


def plot_m(
    summaries: Sequence[MetricSummary],
    output: Path,
    *,
    log_x: bool = False,
    log_y: bool = False,
) -> None:
    """Guarda medias y un desvío estándar como barras de error."""

    if not summaries:
        raise MetricsError("no hay resúmenes para graficar")
    if log_y and any(summary.mean_time_ns <= 0 for summary in summaries):
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

    series: dict[SeriesKey, list[MetricSummary]] = defaultdict(list)
    for summary in summaries:
        series[_series_key(summary)].append(summary)

    figure, axes = plt.subplots(figsize=(8, 5))
    for key in sorted(
        series,
        key=lambda item: (
            item.particle_count,
            item.seed,
            item.boundary,
            item.side,
            item.cutoff,
        ),
    ):
        points = sorted(
            series[key], key=lambda item: item.group.cells_per_side
        )
        cells = [point.group.cells_per_side for point in points]
        means_us = [point.mean_time_ns / 1_000.0 for point in points]
        deviations_us = [
            point.stddev_time_ns / 1_000.0 for point in points
        ]
        label = (
            f"N={key.particle_count}, L={key.side:g}, "
            f"rc={key.cutoff:g}, {key.boundary}, seed={key.seed}"
        )
        axes.errorbar(
            cells,
            means_us,
            yerr=deviations_us,
            marker="o",
            linestyle="-",
            capsize=3,
            label=label,
        )

    axes.set_xlabel("M (celdas por lado)")
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
