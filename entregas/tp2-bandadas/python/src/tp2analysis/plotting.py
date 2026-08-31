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
        0.32: (r"1/\pi", 32),
        0.16: (r"1/(2\pi)", 16),
        0.11: (r"1/(3\pi)", 11),
    }
    for actual, (symbol, count) in low_density_labels.items():
        if abs(density - actual) < 1e-12:
            return (
                rf"$\rho \simeq {symbol}$ (${density:g}$, $N={count}$)"
            )
    return rf"$\rho={density:g}$"


def _model_label(model: str) -> str:
    return {"vicsek": "Vicsek", "voter": "Votante"}.get(model, model)


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
            f"{_model_label(first.model)}, {_density_label(first.density)}, "
            rf"$\eta={first.eta:g}$, semilla ${first.seed}$"
        )
        times = [row.time for row in values]
        axes[0].plot(times, [row.polarization for row in values], label=label)
        axes[1].plot(
            times,
            [row.largest_cluster_fraction for row in values],
            label=label,
        )
    axes[0].set_ylabel(r"Polarización $v_a$")
    axes[1].set_ylabel(r"Fracción de la componente gigante $S$")
    axes[1].set_xlabel(r"Tiempo $t$")
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
                    label=rf"Inicio del estacionario $t_0={start:g}$",
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
        label = (
            f"{_model_label(model)}, {_density_label(density)}, "
            rf"$\eta={eta:g}$, semilla ${seed}$"
        )
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
    axes[0].set_ylabel(r"Media por bloque de $v_a$")
    axes[1].set_ylabel(r"Media por bloque de $S$")
    axes[1].set_xlabel(r"Centro del bloque temporal $t$")
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
            ylabel = r"Polarización estacionaria $\langle v_a \rangle$"
        else:
            means = [value.cluster_mean for value in values]
            errors = [value.cluster_std for value in values]
            ylabel = r"Componente gigante estacionaria $\langle S \rangle$"
        axis.errorbar(
            [value.eta for value in values],
            means,
            yerr=errors,
            marker="o",
            capsize=3,
            label=f"{_model_label(model)}, {_density_label(density)}",
        )
    axis.set_xlabel(r"Ruido normalizado $\eta$")
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
    invert_axes: bool = False,
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
        cluster = [value.cluster_mean for value in values]
        polarization = [value.polarization_mean for value in values]
        axis.plot(
            polarization if invert_axes else cluster,
            cluster if invert_axes else polarization,
            marker="o",
            label=f"{_model_label(model)}, {_density_label(density)}",
        )
    if invert_axes:
        axis.set_xlabel(r"Polarización $\langle v_a \rangle$")
        axis.set_ylabel(r"Fracción de la componente gigante $\langle S \rangle$")
    else:
        axis.set_xlabel(r"Fracción de la componente gigante $\langle S \rangle$")
        axis.set_ylabel(r"Polarización $\langle v_a \rangle$")
    axis.set_xlim(-0.03, 1.03)
    axis.set_ylim(-0.03, 1.03)
    axis.legend()
    axis.grid(alpha=0.25)
    figure.tight_layout()
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180)
    plt.close(figure)
