#!/usr/bin/env python3
"""Genera gráficos legibles para la presentación a partir de los datos del informe."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "experiments" / "raw" / "production"
LOW = ROOT / "experiments" / "raw" / "cluster-production"
RESULTS = ROOT / "experiments" / "results"
OUT = ROOT / "presentacion" / "figuras"
TP1 = ROOT.parent / "tp1-cim" / "experiments" / "results" / "summary-n-periodic.csv"
T0 = 4000

COLORS = {2.0: "#0072B2", 4.0: "#E69F00", 8.0: "#009E73"}
LOW_COLORS = {0.11: "#0072B2", 0.16: "#E69F00", 0.32: "#009E73"}


def configure() -> None:
    plt.rcParams.update(
        {
            "font.size": 16,
            "axes.labelsize": 18,
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
            "legend.fontsize": 12,
            "lines.linewidth": 2.0,
            "lines.markersize": 7,
            "figure.dpi": 180,
            "savefig.dpi": 220,
        }
    )


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def save(figure: plt.Figure, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(OUT / name, bbox_inches="tight")
    plt.close(figure)


def time_series_polarization(model: str, etas: list[str], name: str) -> None:
    figure, axis = plt.subplots(figsize=(8.4, 4.6))
    for eta in etas:
        path = RAW / f"{model}-rho4-eta{eta}-seed1-observables.csv"
        rows = read_rows(path)[::5]
        label = eta.replace("p", ",")
        axis.plot(
            [float(row["time"]) for row in rows],
            [float(row["polarization"]) for row in rows],
            label=rf"$\eta={label}$",
        )
    axis.axvline(T0, color="black", linestyle="--", linewidth=1.8, label=rf"$t_0={T0}$")
    axis.set_xlabel("Tiempo (pasos)")
    axis.set_ylabel(r"Polarización $v_a$")
    axis.set_ylim(-0.03, 1.03)
    axis.grid(alpha=0.25)
    axis.legend(ncol=2, loc="lower right")
    save(figure, name)


def time_series_density(base: Path, files: list[tuple[str, str]], name: str) -> None:
    figure, axes = plt.subplots(2, 1, sharex=True, figsize=(8.4, 6.1))
    for filename, label in files:
        rows = read_rows(base / filename)[::5]
        times = [float(row["time"]) for row in rows]
        axes[0].plot(times, [float(row["polarization"]) for row in rows], label=label)
        axes[1].plot(times, [float(row["largest_cluster_fraction"]) for row in rows], label=label)
    for axis in axes:
        axis.axvline(T0, color="black", linestyle="--", linewidth=1.6)
        axis.set_ylim(-0.03, 1.03)
        axis.grid(alpha=0.25)
    axes[0].set_ylabel(r"Polarización $v_a$")
    axes[1].set_ylabel(r"Componente gigante $S$")
    axes[1].set_xlabel("Tiempo (pasos)")
    axes[0].legend(ncol=3, loc="lower right")
    save(figure, name)


def density_label(density: float, low: bool) -> str:
    if not low:
        return rf"$\rho={density:g}$"
    counts = {0.11: 11, 0.16: 16, 0.32: 32}
    return rf"$N={counts[round(density, 2)]}$"


def plot_eta(summary_path: Path, observable: str, name: str, low: bool = False) -> None:
    grouped: dict[tuple[str, float], list[dict[str, str]]] = defaultdict(list)
    for row in read_rows(summary_path):
        grouped[(row["model"], float(row["density"]))].append(row)
    figure, axis = plt.subplots(figsize=(8.5, 5.3))
    palette = LOW_COLORS if low else COLORS
    for (model, density), values in sorted(grouped.items()):
        values.sort(key=lambda row: float(row["eta"]))
        mean_key = "polarization_mean" if observable == "polarization" else "cluster_mean"
        std_key = "polarization_std" if observable == "polarization" else "cluster_std"
        axis.errorbar(
            [float(row["eta"]) for row in values],
            [float(row[mean_key]) for row in values],
            yerr=[float(row[std_key]) for row in values],
            color=palette[round(density, 2)],
            marker="o" if model == "vicsek" else "s",
            linestyle="-" if model == "vicsek" else "--",
            capsize=4,
            label=("Vicsek, " if model == "vicsek" else "Votante, ")
            + density_label(density, low),
        )
    axis.set_xlabel(r"Ruido normalizado $\eta$")
    axis.set_ylabel(
        r"Polarización media $\langle v_a\rangle$"
        if observable == "polarization"
        else r"Componente gigante media $\langle S\rangle$"
    )
    axis.set_ylim(-0.03, 1.03)
    axis.grid(alpha=0.25)
    axis.legend(ncol=2, loc="best")
    save(figure, name)


def plot_va_s(summary_path: Path, name: str, low: bool = False) -> None:
    grouped: dict[tuple[str, float], list[dict[str, str]]] = defaultdict(list)
    for row in read_rows(summary_path):
        grouped[(row["model"], float(row["density"]))].append(row)
    figure, axis = plt.subplots(figsize=(6.6, 5.8))
    palette = LOW_COLORS if low else COLORS
    for (model, density), values in sorted(grouped.items()):
        values.sort(key=lambda row: float(row["eta"]))
        axis.plot(
            [float(row["polarization_mean"]) for row in values],
            [float(row["cluster_mean"]) for row in values],
            color=palette[round(density, 2)],
            marker="o" if model == "vicsek" else "s",
            linestyle="-" if model == "vicsek" else "--",
            label=("V, " if model == "vicsek" else "vot, ")
            + density_label(density, low),
        )
    axis.set_xlabel(r"Polarización media $\langle v_a\rangle$")
    axis.set_ylabel(r"Componente gigante media $\langle S\rangle$")
    axis.set_xlim(-0.03, 1.03)
    axis.set_ylim(-0.03, 1.03)
    axis.grid(alpha=0.25)
    axis.legend(fontsize=10, ncol=2, loc="best")
    save(figure, name)


def plot_cim() -> None:
    figure, axis = plt.subplots(figsize=(8.5, 5.3))
    tp1_rows = [
        row
        for row in read_rows(TP1)
        if row["boundary"] == "periodic" and row["method"] == "cim"
    ]
    for regime, label, color in (
        ("fixed", r"TP1: $\rho=1{,}25$", "#0072B2"),
        ("free", r"TP1: $L=20$", "#56B4E9"),
    ):
        values = sorted(
            (row for row in tp1_rows if row["regime"] == regime),
            key=lambda row: int(row["N"]),
        )
        axis.errorbar(
            [int(row["N"]) for row in values],
            [float(row["mean_time_ns"]) / 1000 for row in values],
            yerr=[float(row["stddev_time_ns"]) / 1000 for row in values],
            color=color,
            marker="x",
            linestyle="--",
            capsize=4,
            label=label,
        )
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_rows(RESULTS / "cim-summary.csv"):
        grouped[row["model"]].append(row)
    for model, color in (("vicsek", "#009E73"), ("voter", "#D55E00")):
        values = sorted(grouped[model], key=lambda row: int(row["particle_count"]))
        axis.errorbar(
            [int(row["particle_count"]) for row in values],
            [float(row["mean_time_ns"]) / 1000 for row in values],
            yerr=[float(row["stddev_time_ns"]) / 1000 for row in values],
            color=color,
            marker="o",
            capsize=4,
            label="TP2: " + ("Vicsek" if model == "vicsek" else "votante"),
        )
    axis.set_xlabel("Cantidad de partículas")
    axis.set_ylabel(r"Tiempo de búsqueda ($\mu$s)")
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.grid(alpha=0.25, which="both")
    axis.legend(ncol=2, loc="upper left")
    save(figure, "cim-presentacion.png")


def main() -> None:
    configure()
    time_series_polarization("vicsek", ["0", "0p5", "1"], "serie-va-vicsek-presentacion.png")
    time_series_polarization("voter", ["0", "0p05", "0p25"], "serie-va-votante-presentacion.png")
    time_series_density(
        RAW,
        [
            ("vicsek-rho2-eta0p5-seed1-observables.csv", r"$\rho=2$"),
            ("vicsek-rho4-eta0p5-seed1-observables.csv", r"$\rho=4$"),
            ("vicsek-rho8-eta0p5-seed1-observables.csv", r"$\rho=8$"),
        ],
        "series-densidades-presentacion.png",
    )
    time_series_density(
        LOW,
        [
            ("vicsek-rho0p32-eta0p25-seed1-observables.csv", r"$N=32$"),
            ("vicsek-rho0p16-eta0p25-seed1-observables.csv", r"$N=16$"),
            ("vicsek-rho0p11-eta0p25-seed1-observables.csv", r"$N=11$"),
        ],
        "series-baja-densidad-presentacion.png",
    )
    plot_eta(RESULTS / "summary-densidades.csv", "polarization", "va-vs-eta-presentacion.png")
    plot_eta(RESULTS / "summary-densidades.csv", "cluster", "s-vs-eta-presentacion.png")
    plot_eta(
        RESULTS / "summary-baja-densidad.csv",
        "cluster",
        "s-vs-eta-baja-presentacion.png",
        low=True,
    )
    plot_va_s(RESULTS / "summary-densidades.csv", "va-vs-s-presentacion.png")
    plot_va_s(
        RESULTS / "summary-baja-densidad.csv",
        "va-vs-s-baja-presentacion.png",
        low=True,
    )
    plot_cim()


if __name__ == "__main__":
    main()
