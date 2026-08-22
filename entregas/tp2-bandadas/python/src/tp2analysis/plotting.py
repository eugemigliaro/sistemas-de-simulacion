from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .data import Observation
from .stats import Summary


def _pyplot():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def plot_time_series(
    observations: Iterable[Observation],
    output: str | Path,
    stationary_start: float | None = None,
) -> None:
    rows = list(observations)
    if not rows:
        raise ValueError("no hay observaciones")
    plt = _pyplot()
    figure, axes = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
    times = [row.time for row in rows]
    axes[0].plot(times, [row.polarization for row in rows])
    axes[0].set_ylabel("Polarización va")
    axes[1].plot(times, [row.largest_cluster_fraction for row in rows])
    axes[1].set_ylabel("Componente gigante S")
    axes[1].set_xlabel("Tiempo")
    if stationary_start is not None:
        for axis in axes:
            axis.axvline(
                stationary_start,
                color="black",
                linestyle="--",
                label="Inicio estacionario",
            )
        axes[0].legend()
    figure.tight_layout()
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def plot_eta(
    summaries: Iterable[Summary],
    output: str | Path,
    observable: str,
) -> None:
    if observable not in {"polarization", "cluster"}:
        raise ValueError("observable debe ser polarization o cluster")
    grouped: dict[tuple[str, float], list[Summary]] = defaultdict(list)
    for summary in summaries:
        grouped[(summary.model, summary.density)].append(summary)
    if not grouped:
        raise ValueError("no hay resúmenes")

    plt = _pyplot()
    figure, axis = plt.subplots(figsize=(8, 5))
    for (model, density), values in sorted(grouped.items()):
        values.sort(key=lambda value: value.eta)
        if observable == "polarization":
            means = [value.polarization_mean for value in values]
            errors = [value.polarization_std for value in values]
            ylabel = "Polarización estacionaria"
        else:
            means = [value.cluster_mean for value in values]
            errors = [value.cluster_std for value in values]
            ylabel = "Componente gigante estacionaria S"
        axis.errorbar(
            [value.eta for value in values],
            means,
            yerr=errors,
            marker="o",
            capsize=3,
            label=f"{model}, rho={density:g}",
        )
    axis.set_xlabel("Ruido normalizado eta")
    axis.set_ylabel(ylabel)
    axis.set_ylim(-0.03, 1.03)
    axis.legend()
    axis.grid(alpha=0.25)
    figure.tight_layout()
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def plot_polarization_vs_cluster(
    summaries: Iterable[Summary],
    output: str | Path,
) -> None:
    grouped: dict[tuple[str, float], list[Summary]] = defaultdict(list)
    for summary in summaries:
        grouped[(summary.model, summary.density)].append(summary)
    if not grouped:
        raise ValueError("no hay resúmenes")
    plt = _pyplot()
    figure, axis = plt.subplots(figsize=(7, 6))
    for (model, density), values in sorted(grouped.items()):
        values.sort(key=lambda value: value.eta)
        axis.plot(
            [value.cluster_mean for value in values],
            [value.polarization_mean for value in values],
            marker="o",
            label=f"{model}, rho={density:g}",
        )
    axis.set_xlabel("Componente gigante S")
    axis.set_ylabel("Polarización va")
    axis.set_xlim(-0.03, 1.03)
    axis.set_ylim(-0.03, 1.03)
    axis.legend()
    axis.grid(alpha=0.25)
    figure.tight_layout()
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180)
    plt.close(figure)
