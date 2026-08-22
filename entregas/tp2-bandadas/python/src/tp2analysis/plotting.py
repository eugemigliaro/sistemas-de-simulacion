from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .data import Observation, observation_run_key
from .stats import BlockSummary, StationaryStarts, Summary


def _pyplot():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _density_label(density: float) -> str:
    low_density_labels = {
        0.32: "1/pi (real=0.32, N=32)",
        0.16: "1/(2*pi) (real=0.16, N=16)",
        0.11: "1/(3*pi) (real=0.11, N=11)",
    }
    for actual, label in low_density_labels.items():
        if abs(density - actual) < 1e-12:
            return f"rho~{label}"
    return f"rho={density:g}"


def plot_time_series(
    observations: Iterable[Observation],
    output: str | Path,
    stationary_start: float | StationaryStarts | None = None,
) -> None:
    rows = list(observations)
    if not rows:
        raise ValueError("no hay observaciones")
    grouped: dict[tuple, list[Observation]] = defaultdict(list)
    for row in rows:
        grouped[observation_run_key(row)].append(row)
    plt = _pyplot()
    figure, axes = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
    for values in grouped.values():
        values.sort(key=lambda row: row.time)
        first = values[0]
        label = (
            f"{first.model}, {_density_label(first.density)}, "
            f"eta={first.eta:g}, semilla={first.seed}"
        )
        times = [row.time for row in values]
        axes[0].plot(times, [row.polarization for row in values], label=label)
        axes[1].plot(
            times,
            [row.largest_cluster_fraction for row in values],
            label=label,
        )
    axes[0].set_ylabel("Polarización va")
    axes[1].set_ylabel("Componente gigante S")
    axes[1].set_xlabel("Tiempo")
    if stationary_start is not None:
        starts: set[float] = set()
        for values in grouped.values():
            first = values[0]
            if isinstance(stationary_start, (int, float)):
                starts.add(float(stationary_start))
            else:
                key = (first.model, first.density, first.eta)
                if key not in stationary_start:
                    raise ValueError(f"falta inicio estacionario para {key}")
                starts.add(float(stationary_start[key]))
        for start in sorted(starts):
            for axis in axes:
                axis.axvline(
                    start,
                    color="black",
                    linestyle="--",
                    alpha=0.75,
                    label=f"Inicio estacionario t={start:g}",
                )
    for axis in axes:
        axis.legend(fontsize="small")
        axis.grid(alpha=0.2)
    figure.tight_layout()
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def plot_blocks(
    blocks: Iterable[BlockSummary],
    output: str | Path,
) -> None:
    rows = list(blocks)
    if not rows:
        raise ValueError("no hay bloques")
    grouped: dict[tuple[str, float, float, int], list[BlockSummary]] = defaultdict(list)
    for row in rows:
        grouped[(row.model, row.density, row.eta, row.seed)].append(row)

    plt = _pyplot()
    figure, axes = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
    for (model, density, eta, seed), values in sorted(grouped.items()):
        values.sort(key=lambda row: row.block_start)
        centers = [(row.block_start + row.block_end) / 2 for row in values]
        label = f"{model}, {_density_label(density)}, eta={eta:g}, semilla={seed}"
        axes[0].errorbar(
            centers,
            [row.polarization_mean for row in values],
            yerr=[row.polarization_std for row in values],
            marker="o",
            capsize=3,
            label=label,
        )
        axes[1].errorbar(
            centers,
            [row.cluster_mean for row in values],
            yerr=[row.cluster_std for row in values],
            marker="o",
            capsize=3,
            label=label,
        )
    axes[0].set_ylabel("Media por bloque de va")
    axes[1].set_ylabel("Media por bloque de S")
    axes[1].set_xlabel("Centro del bloque temporal")
    for axis in axes:
        axis.set_ylim(-0.03, 1.03)
        axis.grid(alpha=0.2)
        axis.legend(fontsize="small")
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
            label=f"{model}, {_density_label(density)}",
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
            label=f"{model}, {_density_label(density)}",
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
