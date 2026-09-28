#!/usr/bin/env python3
"""Construye las figuras de la presentación del TP3 desde los resultados.

No corre simulaciones: lee las tablas de ``experiments/results`` y los archivos
de obstáculos. Los fotogramas de las animaciones los escribe
``barridos_presentacion.py animaciones``.
"""

from __future__ import annotations

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
from matplotlib.patches import Circle, Rectangle  # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments/results"
ELIPSES = RESULTS / "elipses"
PRESENTACION = RESULTS / "presentacion"
FIGURES = ROOT / "presentacion/figuras"
CONFIGS = ROOT / "experiments/raw/elipses/configs"
sys.path.insert(0, str(ROOT / "scripts"))

L, W, D = 1.20, 0.68, 0.20

# Paleta categórica validada (orden fijo, familias distinguibles también con
# daltonismo); cada familia lleva además su propia forma de marcador.
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
VIOLET = "#4a3aa7"
INK = "#0b0b0b"
MUTED = "#52514e"
OBSTACLE = "#d35c20"
GOAL = "#005b91"

# Las figuras se proyectan durante la exposición: ejes y leyendas deben
# conservarse legibles aun cuando se inserten en una diapositiva.
plt.rcParams.update({
    "font.size": 14,
    "axes.labelsize": 16,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 13,
})

ELEGIDA = "super_P277_B268_p472_s113_rho175"
FAMILIAS = {
    "disco_unico": ("disco único", BLUE, "o"),
    "elipse_focos_fijos": ("elipses con focos fijos", ORANGE, "s"),
    "elipse_separada": ("elipses separadas", AQUA, "^"),
    "superelipse": ("superelipses", VIOLET, "D"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def finish(fig, name: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / name, bbox_inches="tight")
    plt.close(fig)


def obstacles(label: str) -> list[tuple[float, float, float]]:
    """Obstáculos de una configuración; se regeneran si faltan."""
    if label == "vacia":
        return []
    path = CONFIGS / f"{label}.txt"
    if not path.exists():
        import busqueda_elipses as be
        diseno = be.diseno_desde(_row_for(label))
        be.construir(diseno)
    return [tuple(map(float, line.split())) for line in path.read_text().splitlines() if line]


def _row_for(label: str) -> dict[str, object]:
    for name in ("plan_super_final.csv", "plan_final.csv", "plan_separacion_final_extendida.csv",
                 "plan_barrido.csv"):
        path = ELIPSES / name
        if path.exists():
            for row in read_csv(path):
                if row["label"] == label:
                    return row
    raise KeyError(label)


def draw_table(axis, discs: list[tuple[float, float, float]], lw: float = 1.2) -> None:
    axis.add_patch(Rectangle((0, 0), L, W, fill=False, lw=lw, color=INK))
    for x in (0, L):
        axis.plot([x, x], [(W - D) / 2, (W + D) / 2], color=GOAL, lw=3 * lw,
                  solid_capstyle="butt")
    for x, y, r in discs:
        axis.add_patch(Circle((x, y), r, facecolor=OBSTACLE, edgecolor="none"))
    axis.set_xlim(-0.03, L + 0.03)
    axis.set_ylim(-0.03, W + 0.03)
    axis.set_aspect("equal")
    axis.axis("off")


def runtime_figure(values: dict[str, object]) -> None:
    path = RESULTS / "runtime_saturacion.csv"
    if not path.exists():
        print("falta runtime_saturacion.csv: se omite la figura de tiempo de ejecución")
        return
    rows = read_csv(path)
    finished: dict[tuple[int, str], list[dict[str, str]]] = defaultdict(list)
    unfinished: dict[int, int] = defaultdict(int)
    for row in rows:
        n = int(row["particle_count"])
        if row["finished"] == "1":
            finished[(n, row["layout"])].append(row)
        else:
            unfinished[n] += 1

    # Tiempo total = eventos × costo por evento. Los paneles de la derecha
    # separan los dos factores: la frecuencia de choques, que diverge cerca del
    # empaquetamiento compacto, y el costo de cada evento, que crece con N.
    fig = plt.figure(figsize=(11.5, 4.6), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, width_ratios=(1.55, 1.0))
    total = fig.add_subplot(grid[:, 0])
    rate = fig.add_subplot(grid[0, 1])
    cost = fig.add_subplot(grid[1, 1], sharex=rate)
    styles = (("random", BLUE, "o", "posiciones al azar"),
              ("triangular", ORANGE, "s", "red triangular"))
    for layout, color, marker, label in styles:
        keys = sorted(k for k in finished if k[1] == layout)
        ns = np.array([k[0] for k in keys])
        runtime = [np.array([float(r["runtime_seconds"]) for r in finished[k]]) for k in keys]
        events = [np.array([int(r["events"]) for r in finished[k]]) for k in keys]
        total.errorbar(ns, [t.mean() for t in runtime], yerr=[t.std(ddof=1) for t in runtime],
                       fmt=marker, ms=7, color=color, capsize=4, label=f"{label}: media ± desvío")
        rate.plot(ns, [e.mean() / 30.0 / n for e, n in zip(events, ns)], marker, ms=6,
                  color=color)
        cost.plot(ns, [(t / e).mean() * 1e6 for t, e in zip(runtime, events)], marker, ms=6,
                  color=color)
    if unfinished:
        ns = sorted(unfinished)
        total.scatter(ns, [600.0] * len(ns), marker="x", s=90, color=INK, zorder=5,
                      label="no terminó en 10 min")
    total.axhline(600.0, color=MUTED, ls="--", lw=1.2)
    total.text(15, 600.0 * 1.35, "corte: 10 min", color=MUTED, fontsize=13)
    for axis in (total, rate, cost):
        axis.axvline(446, color=MUTED, ls=":", lw=1.2)
        axis.grid(True, which="both", alpha=0.2)
    total.text(455, 1.2, "máximo al azar\n(446)", color=MUTED, fontsize=12, ha="left")
    total.set(yscale="log", xlabel="Cantidad de partículas, N",
              ylabel="Tiempo de ejecución [s]", xlim=(0, 760), ylim=(1e-4, 5e3))
    total.legend(frameon=True, facecolor="white", edgecolor="none", loc="lower right",
                 fontsize=12)
    rate.axvline(737, color=INK, ls="--", lw=1.2)
    rate.text(728, 3.0, "compacto\n(737)", color=INK, fontsize=11, ha="right", va="bottom")
    rate.set(yscale="log", ylabel="choques por\npartícula por s", xlim=(0, 760))
    rate.tick_params(labelbottom=False)
    cost.set(xlabel="Cantidad de partículas, N", ylabel="costo por\nevento [µs]", ylim=(0, None))
    finish(fig, "runtime-vs-N.pdf")
    all_finished = sorted({k[0] for k in finished})
    values["runtime_max_n_finished"] = max(all_finished)
    values["runtime_min_n_unfinished"] = min(unfinished) if unfinished else None


def fu_map_figure(values: dict[str, object]) -> None:
    summary = read_csv(PRESENTACION / "t90_summary_disco.csv")
    curves = read_csv(PRESENTACION / "fu_disco.csv")
    radii = [float(row["radius_m"]) for row in summary]
    times = np.array(sorted({float(row["time_s"]) for row in curves}))
    grid = np.zeros((len(radii), times.size))
    index = {t: i for i, t in enumerate(times)}
    rows = {r: i for i, r in enumerate(radii)}
    for row in curves:
        grid[rows[float(row["radius_m"])], index[float(row["time_s"])]] = float(row["mean_fu"])

    tmax = 32.0
    keep = times <= tmax
    fig, axis = plt.subplots(figsize=(10.5, 4.6), constrained_layout=True)
    edges_t = np.append(times[keep] - 0.05, times[keep][-1] + 0.05)
    edges_r = np.arange(len(radii) + 1) - 0.5
    # Franjas de 0,1 en un solo tono, de claro a oscuro, para que el
    # corrimiento con R se lea como bordes; la franja F_u >= 0,9 va en el color
    # de acento porque su borde izquierdo es t90.
    ramp = plt.get_cmap("Greys")
    bands = [ramp(x) for x in np.linspace(0.12, 0.88, 9)] + [ORANGE]
    colormap = ListedColormap(bands)
    norm = BoundaryNorm(np.round(np.arange(0.0, 1.01, 0.1), 2), colormap.N)
    mesh = axis.pcolormesh(edges_t, edges_r, grid[:, keep], cmap=colormap, norm=norm,
                           shading="flat", edgecolors="none", antialiased=False,
                           rasterized=True)
    bar = fig.colorbar(mesh, ax=axis, pad=0.01, ticks=np.round(np.arange(0, 1.01, 0.1), 1))
    bar.set_label(r"$\langle F_u(t)\rangle$")
    bar.ax.set_yticklabels([f"{t:.1f}".replace(".", ",") for t in np.arange(0, 1.01, 0.1)])
    means = [float(row["mean_t90_seconds"]) for row in summary]
    sems = [float(row["sem_t90_seconds"]) for row in summary]
    # Azul con borde blanco: contrasta con los grises oscuros y con el naranja.
    # Los puntos caen algo antes del borde naranja porque son dos medidas
    # distintas: el promedio de los t90 de cada realización y el instante en
    # que la curva promedio <Fu> llega a 0,9, que se atrasa porque Fu crece
    # cada vez más lento al acercarse a 1.
    axis.errorbar(means, range(len(radii)), xerr=sems, fmt="o", ms=9, color=BLUE,
                  markeredgecolor="white", markeredgewidth=1.5, ecolor="white",
                  elinewidth=1.8, capsize=4, capthick=1.8,
                  label=r"$\langle t_{90}\rangle$ ± EE")
    axis.set_yticks(range(len(radii)),
                    ["vacía" if r == 0 else f"{r:.2f}" for r in radii])
    axis.set(xlabel="Tiempo, t [s]", ylabel="Radio del disco central, R [m]", xlim=(0, tmax))
    axis.legend(frameon=True, loc="lower right", facecolor="#222222", edgecolor="none",
                labelcolor="white", framealpha=0.9)
    finish(fig, "fu-disco-mapa.pdf")
    values["disco_t90"] = {f"{r:.2f}": (m, s) for r, m, s in zip(radii, means, sems)}
    values["disco_repeticiones"] = int(summary[0]["realizaciones"])


def search_figure(values: dict[str, object]) -> None:
    final = {r["label"]: r for r in read_csv(ELIPSES / "t90_summary_final.csv")}
    desempate = {r["label"]: r for r in read_csv(ELIPSES / "t90_summary_desempate.csv")}
    pared = read_csv(ELIPSES / "t90_runs_pared.csv")
    t_pared = np.array([float(r["t90_seconds"]) for r in pared])
    entries = [
        ("mesa vacía", "vacia", final["vacia"], None),
        ("pared de discos\nen el centro", "cerrado_b400_rho175",
         {"mean_t90_seconds": t_pared.mean(),
          "sem_t90_seconds": t_pared.std(ddof=1) / math.sqrt(t_pared.size)}, None),
        ("elipses con focos\nfijos (la mejor)", "cerrado_b235_rho175",
         final["cerrado_b235_rho175"], None),
        ("disco central\nR = 0,34 m", "actual", desempate["actual"], None),
        ("elipses separadas", "abierto_b300_rho175_d390",
         desempate["abierto_b300_rho175_d390"], None),
        ("superelipse\n(elegida)", ELEGIDA, desempate[ELEGIDA], "elegida"),
    ]
    count = len(entries)
    fig = plt.figure(figsize=(10.5, 5.4))
    top, bottom = 0.97, 0.13
    height = (top - bottom) / count
    main = fig.add_axes((0.42, bottom, 0.55, top - bottom))
    for i, (name, label, row, role) in enumerate(entries):
        y = count - 1 - i
        thumb = fig.add_axes((0.005, bottom + y * height + 0.1 * height, 0.17, 0.8 * height))
        discs = [(0.60, 0.34, 0.34)] if label == "actual" else obstacles(label)
        draw_table(thumb, discs, lw=0.8)
        fig.text(0.185, bottom + (y + 0.5) * height, name, va="center", fontsize=12.5,
                 color=INK)
        mean, sem = float(row["mean_t90_seconds"]), float(row["sem_t90_seconds"])
        color = VIOLET if role == "elegida" else BLUE
        marker = "*" if role == "elegida" else "o"
        main.errorbar([mean], [y], xerr=[sem], fmt=marker, ms=14 if role else 8,
                      color=color, capsize=4)
        main.text(mean + sem + 0.35, y, f"{mean:.2f} ± {sem:.2f} s".replace(".", ","),
                  va="center", fontsize=12, color=MUTED)
    main.set_ylim(-0.5, count - 0.5)
    main.set_yticks([])
    main.set_xlim(11.5, 26.5)
    main.set_xlabel(r"$\langle t_{90}\rangle$ [s]")
    main.grid(True, axis="x", alpha=0.25)
    finish(fig, "busqueda-resumen.pdf")


def depth_figure(values: dict[str, object]) -> None:
    rows = read_csv(PRESENTACION / "t90_summary_profundidad.csv")
    rows.sort(key=lambda r: float(r["profundidad_m"]))
    depth = np.array([float(r["profundidad_m"]) for r in rows])
    mean = np.array([float(r["mean_t90_seconds"]) for r in rows])
    sem = np.array([float(r["sem_t90_seconds"]) for r in rows])
    disco = read_csv(ELIPSES / "t90_summary_desempate.csv")
    disco_mean = float(next(r for r in disco if r["label"] == "actual")["mean_t90_seconds"])

    fig = plt.figure(figsize=(10.5, 5.2))
    axis = fig.add_axes((0.09, 0.13, 0.88, 0.56))
    axis.errorbar(depth, mean, yerr=sem, fmt="o", ms=8, color=VIOLET, capsize=4,
                  label=r"$\langle t_{90}\rangle$ ± EE (24 realizaciones)")
    chosen = np.argmin(abs(depth - 0.277))
    axis.plot(depth[chosen], mean[chosen], "*", ms=18, color=VIOLET, markeredgecolor="white",
              label="elegida")
    axis.axhline(disco_mean, color=BLUE, ls="--", lw=1.4, label="disco central R = 0,34 m")
    axis.set(xlabel="Profundidad de la sala, P [m]", ylabel=r"$\langle t_{90}\rangle$ [s]")
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False, loc="upper center", ncol=3, fontsize=12)
    axis.set_ylim(min(mean - sem) - 0.5, max(max(mean + sem), disco_mean) + 1.3)
    xmin, xmax = axis.get_xlim()
    plan = {r["label"]: r for r in read_csv(PRESENTACION / "plan_profundidad.csv")}
    for target in (depth[0], 0.277, depth[-1]):
        label = next(k for k, r in plan.items() if math.isclose(float(r["profundidad_m"]), target))
        discs = [tuple(map(float, line.split()))
                 for line in (ROOT / plan[label]["ruta"]).read_text().splitlines() if line]
        center = 0.09 + 0.88 * (target - xmin) / (xmax - xmin)
        thumb = fig.add_axes((center - 0.1, 0.72, 0.2, 0.26))
        draw_table(thumb, discs, lw=0.8)
        thumb.set_title(f"P = {target:.2f} m".replace(".", ","), fontsize=12, color=INK, pad=2)
    finish(fig, "t90-vs-profundidad.pdf")
    values["profundidad"] = {f"{d:.3f}": (m, s) for d, m, s in zip(depth, mean, sem)}


def diffusion_figures(values: dict[str, object]) -> None:
    import run_experiments as rx
    window = rx.DIFFUSION_WINDOW
    summary = {r["label"]: r for r in read_csv(ELIPSES / "difusion_todas.csv")}

    fig, axis = plt.subplots(figsize=(6.3, 5.0), constrained_layout=True)
    for label, path, color, name in (
        ("vacia", RESULTS / "msd_vacia.csv", BLUE, "mesa vacía"),
        (ELEGIDA, ELIPSES / f"msd_{ELEGIDA}.csv", VIOLET, "elegida"),
    ):
        rows = read_csv(path)
        t = np.array([float(r["lag_seconds"]) for r in rows])
        msd = np.array([float(r["msd_m2"]) for r in rows])
        spread = np.array([float(r["std_m2"]) for r in rows])
        d = float(summary[label]["pooled_D_m2_s"])
        axis.plot(t, msd, color=color, lw=2, label=f"{name}")
        axis.fill_between(t, msd - spread, msd + spread, color=color, alpha=0.15, lw=0)
        line = np.linspace(0, window[1], 50)
        axis.plot(line, 4 * d * line, "--", color=INK, lw=1.2)
        axis.text(window[1] + 0.05, 4 * d * window[1],
                  f"D = {d:.4f}".replace(".", ",") + r" m$^2$/s", color=color, fontsize=12,
                  va="center")
    axis.axvspan(window[0], window[1], color=MUTED, alpha=0.08)
    axis.set(xlabel="Tiempo, t [s]", ylabel=r"DCM(t) [m$^2$]", xlim=(0, 3.0), ylim=(0, None))
    axis.text(np.mean(window), axis.get_ylim()[1] * 0.965, "ventana de ajuste",
              ha="center", va="top", fontsize=11, color=MUTED)
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False, loc="center right")
    finish(fig, "DCM-ajuste.pdf")

    rows = read_csv(ELIPSES / f"ec_{ELEGIDA}.csv")
    slopes = np.array([float(r["slope_m2_s"]) for r in rows])
    errors = np.array([float(r["squared_error"]) for r in rows])
    minimum = int(np.argmin(errors))
    fig, axis = plt.subplots(figsize=(6.3, 5.0), constrained_layout=True)
    axis.plot(slopes, errors, color=VIOLET, lw=2)
    axis.scatter([slopes[minimum]], [errors[minimum]], color=ORANGE, zorder=4, s=60)
    axis.axvline(slopes[minimum], color=ORANGE, ls="--",
                 label=fr"$c_{{min}}={slopes[minimum]:.4f}$ m$^2$/s".replace(".", "{,}"))
    axis.set(xlabel=r"Pendiente candidata, $c$ [m$^2$/s]", ylabel=r"Error $E(c)$ [m$^4$]")
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False)
    finish(fig, "error-ajuste.pdf")
    elegida = summary[ELEGIDA]
    values["elegida_D"] = (float(elegida["mean_D_m2_s"]), float(elegida["std_D_m2_s"]),
                           float(elegida["pooled_D_m2_s"]))
    values["vacia_D"] = (float(summary["vacia"]["mean_D_m2_s"]),
                         float(summary["vacia"]["std_D_m2_s"]))
    values["difusion_repeticiones"] = rx.DIFFUSION_REPETITIONS


def correlation_figure(values: dict[str, object]) -> None:
    rows = read_csv(ELIPSES / "difusion_todas.csv")
    fig, axis = plt.subplots(figsize=(10.5, 4.6), constrained_layout=True)
    for family, (name, color, marker) in FAMILIAS.items():
        selected = [r for r in rows if r["familia"] == family]
        r_family = np.corrcoef([float(r["mean_D_m2_s"]) for r in selected],
                               [float(r["mean_t90_seconds"]) for r in selected])[0, 1]
        axis.scatter([float(r["mean_D_m2_s"]) for r in selected],
                     [float(r["mean_t90_seconds"]) for r in selected],
                     marker=marker, s=34, color=color, alpha=0.8, linewidths=0,
                     label=f"{name} (n = {len(selected)}, r = {r_family:+.2f})".replace(".", ","))
    for label, name, marker, color in (("vacia", "mesa vacía", "X", INK),
                                       (ELEGIDA, "elegida", "*", VIOLET)):
        row = next(r for r in rows if r["label"] == label)
        axis.errorbar(float(row["mean_D_m2_s"]), float(row["mean_t90_seconds"]),
                      xerr=float(row["std_D_m2_s"]), yerr=float(row["sem_t90_seconds"]),
                      fmt=marker, ms=15, color=color, markeredgecolor="white", capsize=3,
                      zorder=5)
        axis.annotate(name, (float(row["mean_D_m2_s"]), float(row["mean_t90_seconds"])),
                      xytext=(10, -14), textcoords="offset points", fontsize=12, color=INK)
    d = np.array([float(r["mean_D_m2_s"]) for r in rows])
    t = np.array([float(r["mean_t90_seconds"]) for r in rows])
    correlation = float(np.corrcoef(d, t)[0, 1])
    axis.text(0.99, 0.04, fr"todas: $r = {correlation:+.2f}$".replace(".", "{,}"),
              transform=axis.transAxes, ha="right", fontsize=13, color=INK)
    axis.set(xlabel=r"$\langle D\rangle$ [m$^2$/s]", ylabel=r"$\langle t_{90}\rangle$ [s]")
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False, loc="upper right", fontsize=11.5)
    finish(fig, "D-vs-t90.pdf")
    values["pearson_todas"] = correlation
    values["configuraciones_difusion"] = len(rows)


def main() -> int:
    values: dict[str, object] = {}
    runtime_figure(values)
    fu_map_figure(values)
    search_figure(values)
    depth_figure(values)
    diffusion_figures(values)
    correlation_figure(values)
    (PRESENTACION / "valores_presentacion.json").write_text(
        json.dumps(values, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
