"""Material para la consulta con la cátedra sobre los atascos permanentes: dos figuras y
dos animaciones en consulta/. Lee experiments/raw/atascos, experiments/results/atascos.csv
y experiments/raw/animaciones.

Uso: python scripts/build_consulta.py [figuras|videos]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

from common import RAW, RESULTS, ROOT
from tp5analysis import style
from tp5analysis.io import read_run
from tp5analysis.observables import population

import matplotlib.pyplot as plt  # noqa: E402  (después de style, que fija el backend)

OUT = ROOT / "consulta"


def population_curves(out: Path = OUT) -> None:
    figure, axis = plt.subplots(figsize=(8.0, 5.4))
    times = np.linspace(0, 1600, 1601)
    stuck = done = 0
    for path in sorted((RAW / "atascos").glob("noise0_seed*.txt")):
        run = read_run(path)
        clogged = run.summary.get("clogged", 0) == 1
        end = float(run.summary["end_time"])
        valid = times <= end
        curve = population(run, times[valid])
        color = style.ORANGE if clogged else style.BLUE
        label = None
        if clogged and not stuck:
            label = "se traba (sin salidas en 300 s)"
        if not clogged and not done:
            label = "evacúa"
        axis.plot(times[valid], curve, color=color, linewidth=1.6, alpha=0.85, label=label)
        if clogged:
            axis.plot(end, curve[-1], marker="x", color=color, markersize=9, markeredgewidth=2)
            stuck += 1
        else:
            done += 1
    axis.set_xlabel("Tiempo (s)")
    axis.set_ylabel("Agentes adentro")
    axis.set_xlim(0, 1600)
    axis.set_ylim(0, 510)
    axis.legend(loc="lower left")
    style.save(figure, out / "curvas-poblacion-20-semillas")
    print(f"curvas de población: {done} evacúan, {stuck} se traban")


def clog_probability(out: Path = OUT) -> None:
    with open(RESULTS / "atascos.csv") as fh:
        rows = list(csv.DictReader(fh))
    noise = np.array([float(r["noise"]) for r in rows]) * 100
    p = np.array([float(r["p_clog"]) for r in rows]) * 100
    low = np.array([float(r["p_low"]) for r in rows]) * 100
    high = np.array([float(r["p_high"]) for r in rows]) * 100
    runs = [int(r["runs"]) for r in rows]
    figure, axis = plt.subplots(figsize=(7.2, 5.2))
    axis.errorbar(noise, p, yerr=[p - low, high - p], color=style.BLUE, marker="o", capsize=6, linestyle="none")
    for x, y, n in zip(noise, p, runs):
        axis.annotate(f"{n} corridas", (x, y), textcoords="offset points", xytext=(12, -4), fontsize=15,
                      color=style.MUTED)
    axis.set_xlabel("Fluctuación en contacto (% de m v$_d$/τ)")
    axis.set_ylabel("Corridas trabadas (%)")
    axis.set_xticks(noise)
    axis.set_xlim(-2, 24)
    axis.set_ylim(0, 100)
    style.save(figure, out / "probabilidad-atasco")


def compression(out: Path = OUT, source: str = "tsdmd_seed401.txt", every: int = 50) -> None:
    """Superposición de los contactos a menos de 1,5 m de la puerta en función de cuántos
    agentes quedan adentro (hipótesis de la compresión, ver docs/decisiones.md)."""
    from tp5analysis.io import iter_frames

    path = RAW / "animaciones" / source
    run = read_run(path)
    door = np.array([0.5 * float(run.params["side"]), 0.0])
    inside, top, mean = [], [], []
    for frame in iter_frames(path, every=every):
        near = np.linalg.norm(frame.position - door, axis=1) < 1.5
        if near.sum() < 2:
            continue
        x, r = frame.position[near], run.radius[frame.ids[near]]
        xi = r[:, None] + r[None, :] - np.linalg.norm(x[:, None] - x[None, :], axis=2)
        xi = xi[np.triu_indices(len(r), 1)]
        xi = xi[xi > 0]
        if len(xi):
            inside.append(len(frame.ids))
            top.append(100 * xi.max())
            mean.append(100 * xi.mean())
    figure, axis = plt.subplots(figsize=(7.4, 5.2))
    axis.plot(inside, top, linestyle="none", marker="o", markersize=5, color=style.ORANGE, label="máxima")
    axis.plot(inside, mean, linestyle="none", marker="s", markersize=5, color=style.BLUE, label="media")
    axis.set_xlabel("Agentes adentro")
    axis.set_ylabel("Superposición ξ (cm)")
    axis.set_xlim(0, 510)
    axis.set_ylim(0, None)
    axis.legend(loc="upper left")
    style.save(figure, out / "compresion")


def videos() -> None:
    from tp5analysis.animation import animate

    OUT.mkdir(parents=True, exist_ok=True)
    animate(RAW / "animaciones" / "atasco_s104.txt", OUT / "atasco.mp4", every=5, fps=30, color="speed",
            poster=OUT / "atasco.png", poster_time=400.0,
            caption="TSDMD, sin fluctuación: el arco queda quieto y nadie más sale")
    animate(RAW / "animaciones" / "hibrido_s101.txt", OUT / "hibrido.mp4", every=2, fps=30, color="mode",
            until=120.0, poster=OUT / "hibrido.png", poster_time=15.0, caption="Híbrido, T* = 0,05 s")


def main() -> None:
    what = sys.argv[1] if len(sys.argv) > 1 else "todo"
    if what in ("figuras", "todo"):
        population_curves()
        clog_probability()
        compression()
    if what in ("videos", "todo"):
        videos()


if __name__ == "__main__":
    main()
