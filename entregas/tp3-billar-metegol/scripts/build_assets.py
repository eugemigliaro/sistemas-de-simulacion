#!/usr/bin/env python3
"""Construye figuras, fotogramas y videos desde los resultados del TP3."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments/results"
FIGURES = ROOT / "presentacion/figuras"
VIDEOS = ROOT / "videos"
sys.path.insert(0, str(ROOT / "python/src"))

from tp3analysis.animation import render_animation, render_snapshot  # noqa: E402
from tp3analysis.goals import goal_curve, time_to_fraction  # noqa: E402
from tp3analysis.trajectory import read_trajectory  # noqa: E402


BLUE = "#005b91"
ORANGE = "#d35c20"
RED = "#c73e36"
GREEN = "#2d7f5e"


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def finish(fig, name: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / name, bbox_inches="tight")
    plt.close(fig)


def runtime_figure(metadata: dict[str, object]) -> None:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in read_csv("runtime.csv"):
        grouped[int(row["particle_count"])].append(float(row["runtime_seconds"]))
    values = sorted(grouped)
    means = np.array([np.mean(grouped[n]) for n in values])
    stds = np.array([np.std(grouped[n], ddof=1) for n in values])
    selected = np.array(values) >= 50
    alpha, log_a = np.polyfit(np.log(np.array(values)[selected]), np.log(means[selected]), 1)
    fitted = np.exp(log_a) * np.array(values, dtype=float) ** alpha

    fig, axis = plt.subplots(figsize=(8.2, 5.0), constrained_layout=True)
    axis.errorbar(values, means, yerr=stds, fmt="o", color=BLUE, capsize=4,
                  label="media ± desvío estándar (10 semillas)")
    axis.plot(values, fitted, "--", color=ORANGE, label=fr"ajuste $t\propto N^{{{alpha:.2f}}}$, $N\geq50$")
    axis.set(xscale="log", yscale="log", xlabel="Cantidad de partículas, N",
             ylabel="Tiempo de ejecución [s]")
    axis.grid(True, which="both", alpha=0.25)
    axis.legend(frameon=False)
    finish(fig, "runtime-vs-N.pdf")
    metadata["runtime_exponent"] = float(alpha)
    metadata["runtime_n400_mean_seconds"] = float(means[-1])
    metadata["runtime_n400_std_seconds"] = float(stds[-1])


def goal_figure(selection: dict[str, object]) -> None:
    fig, axis = plt.subplots(figsize=(8.2, 5.0), constrained_layout=True)
    for role, color, label in (
        ("vacia", BLUE, "mesa vacía"),
        ("mejor", ORANGE, "configuración elegida"),
    ):
        item = selection[role]
        trajectory = read_trajectory(ROOT / item["search_trajectory"])
        curve = goal_curve(trajectory)
        result = time_to_fraction(trajectory)
        axis.step(curve.times, curve.goals / curve.particle_count, where="post",
                  color=color, lw=2.0, label=label)
        assert result.t90 is not None
        axis.axvline(result.t90, color=color, ls=":", alpha=0.8)
        axis.text(result.t90 + 0.25, 0.12 if role == "vacia" else 0.04,
                  fr"$t_{{90}}={result.t90:.2f}$ s", color=color)
    axis.axhline(0.9, color="black", ls="--", lw=1.0, label=r"$F_u=0{,}9$")
    axis.set(xlabel="Tiempo [s]", ylabel=r"Fracción usada, $F_u(t)$",
             xlim=(0, 32), ylim=(0, 1.02))
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False, loc="lower right")
    finish(fig, "Fu-vs-tiempo.pdf")


def search_figure(selection: dict[str, object], metadata: dict[str, object]) -> None:
    rows = read_csv("t90_summary.csv")
    empty = next(row for row in rows if row["label"] == "vacia")
    fig, axis = plt.subplots(figsize=(8.2, 5.0), constrained_layout=True)
    colors = [BLUE, GREEN, ORANGE, RED]
    for x, color in zip((0.30, 0.40, 0.50, 0.60), colors):
        selected = sorted(
            (row for row in rows if row["x_m"] and math.isclose(float(row["x_m"]), x)),
            key=lambda row: float(row["radius_m"]),
        )
        axis.errorbar(
            [float(row["radius_m"]) for row in selected],
            [float(row["mean_t90_seconds"]) for row in selected],
            yerr=[float(row["std_t90_seconds"]) for row in selected],
            marker="o", ms=4, lw=1.2, capsize=2.5, color=color,
            label=fr"$x_k={x:.2f}$ m",
        )
    empty_mean = float(empty["mean_t90_seconds"])
    empty_std = float(empty["std_t90_seconds"])
    axis.axhline(empty_mean, color="black", ls="--", lw=1.2, label="mesa vacía")
    axis.fill_between([0.04, 0.35], empty_mean - empty_std, empty_mean + empty_std,
                      color="black", alpha=0.07)
    best = selection["best"]
    axis.scatter([best["radius"]], [best["mean_t90_seconds"]], marker="*", s=180,
                 color="#f2b134", edgecolor="black", zorder=5, label="configuración elegida")
    axis.set(xlabel="Radio del obstáculo [m]", ylabel=r"$\langle t_{90}\rangle$ [s]",
             xlim=(0.04, 0.35))
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False, ncol=2, fontsize=9)
    finish(fig, "t90-vs-configuracion.pdf")
    improvement = 100 * (empty_mean - float(best["mean_t90_seconds"])) / empty_mean
    metadata["empty_mean_t90_seconds"] = empty_mean
    metadata["empty_std_t90_seconds"] = empty_std
    metadata["best_improvement_percent"] = improvement


def diffusion_figures(selection: dict[str, object], metadata: dict[str, object]) -> None:
    label = selection["best"]["label"]
    msd_rows = read_csv(f"msd_{label}.csv")
    lags = np.array([float(row["lag_seconds"]) for row in msd_rows])
    msd = np.array([float(row["msd_m2"]) for row in msd_rows])
    spread = np.array([float(row["std_m2"]) for row in msd_rows])
    summaries = {row["label"]: row for row in read_csv("diffusion_summary.csv")}
    summary = summaries[label]
    pooled_d = float(summary["pooled_D_m2_s"])
    mean_d = float(summary["mean_D_m2_s"])
    std_d = float(summary["std_D_m2_s"])
    window = selection["diffusion_window_seconds"]

    fig, axis = plt.subplots(figsize=(6.3, 5.0), constrained_layout=True)
    axis.plot(lags, msd, color=BLUE, lw=2, label="DCM medio (5 semillas)")
    axis.fill_between(lags, msd - spread, msd + spread, color=BLUE, alpha=0.15)
    line_x = np.linspace(0, window[1], 100)
    axis.plot(line_x, 4 * pooled_d * line_x, "--", color=ORANGE,
              label=fr"ajuste $4Dt$, $D={pooled_d:.4f}$ m$^2$/s")
    axis.axvspan(window[0], window[1], color=ORANGE, alpha=0.08,
                 label=fr"ventana [{window[0]:.1f}, {window[1]:.1f}] s")
    axis.set(xlabel="Desfasaje [s]", ylabel=r"DCM [m$^2$]", xlim=(0, 3.0))
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False, fontsize=9)
    finish(fig, "DCM-ajuste.pdf")

    ec_rows = read_csv(f"ec_{label}.csv")
    slopes = np.array([float(row["slope_m2_s"]) for row in ec_rows])
    errors = np.array([float(row["squared_error"]) for row in ec_rows])
    minimum = int(np.argmin(errors))
    fig, axis = plt.subplots(figsize=(6.3, 5.0), constrained_layout=True)
    axis.plot(slopes, errors, color=BLUE, lw=2)
    axis.scatter([slopes[minimum]], [errors[minimum]], color=ORANGE, zorder=4)
    axis.axvline(slopes[minimum], color=ORANGE, ls="--",
                 label=fr"$c_{{min}}={slopes[minimum]:.4f}$ m$^2$/s")
    axis.set(xlabel=r"Pendiente candidata, $c$ [m$^2$/s]",
             ylabel=r"Error $E(c)$ [m$^4$]")
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False)
    finish(fig, "error-ajuste.pdf")
    metadata["best_mean_D_m2_s"] = mean_d
    metadata["best_std_D_m2_s"] = std_d
    metadata["best_pooled_D_m2_s"] = pooled_d


def correlation_figure(metadata: dict[str, object]) -> None:
    t90 = {row["label"]: row for row in read_csv("t90_summary.csv")}
    diffusion = {row["label"]: row for row in read_csv("diffusion_summary.csv")}
    labels = sorted(set(t90) & set(diffusion))
    x = np.array([float(diffusion[label]["mean_D_m2_s"]) for label in labels])
    y = np.array([float(t90[label]["mean_t90_seconds"]) for label in labels])
    xerr = np.array([float(diffusion[label]["sem_D_m2_s"]) for label in labels])
    yerr = np.array([float(t90[label]["sem_t90_seconds"]) for label in labels])
    correlation = float(np.corrcoef(x, y)[0, 1])

    fig, axis = plt.subplots(figsize=(8.2, 5.0), constrained_layout=True)
    for label in labels:
        index = labels.index(label)
        is_empty = label == "vacia"
        is_best = label == "x60_r34"
        color = ORANGE if is_best else ("black" if is_empty else BLUE)
        marker = "*" if is_best else ("s" if is_empty else "o")
        size = 10 if is_best else 5
        axis.errorbar(x[index], y[index], xerr=xerr[index], yerr=yerr[index],
                      fmt=marker, ms=size, color=color, capsize=2, alpha=0.9)
    axis.scatter([], [], marker="s", color="black", label="mesa vacía")
    axis.scatter([], [], marker="*", s=120, color=ORANGE, label="configuración elegida")
    axis.scatter([], [], marker="o", color=BLUE, label="resto del barrido")
    axis.text(0.98, 0.95, fr"Pearson $r={correlation:.2f}$", ha="right", va="top",
              transform=axis.transAxes,
              bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"})
    axis.set(xlabel=r"$\langle D\rangle$ [m$^2$/s]",
             ylabel=r"$\langle t_{90}\rangle$ [s]")
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False)
    finish(fig, "D-vs-t90.pdf")
    metadata["diffusion_t90_pearson_r"] = correlation


def visual_assets(selection: dict[str, object], videos: bool) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    VIDEOS.mkdir(parents=True, exist_ok=True)
    for role in ("vacia", "mejor"):
        trajectory = read_trajectory(ROOT / selection[role]["trajectory"])
        event_frames = np.flatnonzero(np.array(trajectory.reasons) != "final")
        target = float(selection[role]["t90_seconds"]) * 0.65
        frame = int(event_frames[np.argmin(abs(trajectory.times[event_frames] - target))])
        render_snapshot(trajectory, FIGURES / f"anim-{role}.png", frame)
        if videos:
            render_animation(trajectory, VIDEOS / f"anim-{role}.mp4", fps=30, duration=15)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-videos", action="store_true")
    arguments = parser.parse_args()
    selection = json.loads((RESULTS / "selection.json").read_text(encoding="utf-8"))
    metadata: dict[str, object] = {}
    runtime_figure(metadata)
    goal_figure(selection)
    search_figure(selection, metadata)
    diffusion_figures(selection, metadata)
    correlation_figure(metadata)
    visual_assets(selection, not arguments.skip_videos)
    (RESULTS / "presentation_values.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
