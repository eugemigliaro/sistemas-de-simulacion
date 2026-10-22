#!/usr/bin/env python3
"""Figuras de la presentación a partir de experiments/results.

Siguen la guía de presentaciones: ejes en palabras con unidades, notación
científica con potencias de 10, sin títulos ni captions, tipografía grande y
puntos con símbolo [GPRES, pp. 1-2]. Cada figura se omite si faltan sus datos.
"""
import json
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, LogLocator, NullFormatter, ScalarFormatter  # noqa: E402

from common import DT, FIGURES, RADIUS, RESULTS, ROOT, read_csv  # noqa: E402
from tp4analysis import speed, stats  # noqa: E402

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#dddcd8"
BLUES = LinearSegmentedColormap.from_list("blues", ["#a9cdf5", "#2a78d6", "#0b2f5c"])
AREA = np.pi * RADIUS**2

plt.rcParams.update({
    "font.size": 20, "axes.labelsize": 22, "legend.fontsize": 18, "xtick.labelsize": 19, "ytick.labelsize": 19,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "lines.linewidth": 2.0, "lines.markersize": 9, "legend.frameon": False,
    "savefig.bbox": "tight", "mathtext.default": "regular",
})


def power_of_ten(value, _position=None) -> str:
    if value <= 0:
        return ""
    exponent = np.log10(value)
    if abs(exponent - round(exponent)) > 1e-9:
        mantissa = value / 10 ** np.floor(exponent)
        return rf"${comma(round(mantissa, 6))}\times10^{{{int(np.floor(exponent))}}}$"
    return rf"$10^{{{int(round(exponent))}}}$"


def log_axis(axis, which: str = "both") -> None:
    for name in ("x", "y"):
        if which in (name, "both"):
            getattr(axis, f"set_{name}scale")("log")
            target = getattr(axis, f"{name}axis")
            target.set_major_locator(LogLocator(base=10, numticks=12))
            target.set_major_formatter(FuncFormatter(power_of_ten))
            target.set_minor_formatter(NullFormatter())


def comma(value: float) -> str:
    return f"{value:g}".replace(".", ",")


def save(figure, name: str) -> None:
    """Coma decimal en los ejes lineales, como en el resto de la presentación."""
    for axis in figure.axes:
        for scale, target in ((axis.get_xscale(), axis.xaxis), (axis.get_yscale(), axis.yaxis)):
            if scale == "linear" and isinstance(target.get_major_formatter(), ScalarFormatter):
                target.set_major_formatter(FuncFormatter(lambda value, _: comma(round(value, 10))))
    FIGURES.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURES / f"{name}.pdf")
    figure.savefig(FIGURES / f"{name}.png", dpi=110)
    plt.close(figure)
    print(f"figura {name}")


def number(row: dict, key: str) -> float | None:
    value = row.get(key, "")
    return float(value) if value not in ("", "None") else None


def oscillator() -> None:
    rows = read_csv(RESULTS / "oscillator-ecm.csv")
    figure, axis = plt.subplots(figsize=(7.4, 5.4))
    styles = {
        "beeman": ("Beeman", BLUE, dict(marker="o")),
        "verlet": ("Verlet original", ORANGE, dict(marker="s", markerfacecolor="none", markeredgewidth=2,
                                                    markersize=13)),
        "velocity-verlet": ("Velocity Verlet", AQUA, dict(marker="x", markeredgewidth=2.5, markersize=10)),
        "euler-pc": ("Euler predictor-corrector", YELLOW, dict(marker="^")),
    }
    inset = axis.inset_axes((0.68, 0.05, 0.3, 0.4))
    for key, (label, color, style) in styles.items():
        data = sorted((float(r["dt_s"]), float(r["ecm_m2"])) for r in rows if r["integrator"] == key)
        axis.plot(*zip(*data), color=color, label=label, linewidth=1.5, **style)
        if key != "euler-pc":
            inset.plot(*zip(*data), color=color, linewidth=1.5, **style)
    log_axis(axis)
    inset.set_xscale("log")
    inset.set_yscale("log")
    inset.set_xlim(9e-5, 1.1e-4)
    inset.set_ylim(2.5e-14, 5.6e-14)
    inset.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)
    inset.grid(False)
    for spine in inset.spines.values():
        spine.set_visible(True)
    axis.indicate_inset_zoom(inset, edgecolor=MUTED)
    axis.set_xlabel("Paso temporal (s)")
    axis.set_ylabel("Error cuadrático medio (m²)")
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=17, columnspacing=1.0,
                handlelength=1.6)
    save(figure, "oscilador-ecm")


def energy() -> None:
    series = np.load(RESULTS / "energy-series.npz")
    figure, axis = plt.subplots(figsize=(7.4, 5.0))
    steps = series["steps"]
    for index, (dt, deviation) in enumerate(zip(steps, series["deviation"])):
        color = BLUES(index / max(1, len(steps) - 1))
        valid = np.isfinite(deviation) & (deviation > 0)
        axis.plot(series["times"][valid], deviation[valid], color=color, linewidth=1.4,
                  label=power_of_ten(dt) + " s")
    axis.set_yscale("log")
    axis.yaxis.set_major_locator(LogLocator(base=10, numticks=12))
    axis.yaxis.set_major_formatter(FuncFormatter(power_of_ten))
    axis.yaxis.set_minor_formatter(NullFormatter())
    axis.set_ylim(1e-10, 2)
    axis.set_xlim(0, 300)
    axis.set_xlabel("Tiempo (s)")
    axis.set_ylabel("Variación relativa\nde la energía total")
    axis.legend(title="Paso temporal", loc="lower right", ncol=3, fontsize=14, title_fontsize=15,
                columnspacing=0.8, handlelength=1.2)
    save(figure, "energia-tiempo")

    rows = [r for r in read_csv(RESULTS / "energy-summary.csv") if number(r, "delta_e_mean") is not None]
    figure, axis = plt.subplots(figsize=(6.8, 5.0))
    dt = np.array([float(r["dt_s"]) for r in rows])
    mean = np.array([float(r["delta_e_mean"]) for r in rows])
    std = np.array([float(r["delta_e_std"]) for r in rows])
    axis.errorbar(dt, mean, yerr=std, color=BLUE, marker="o", capsize=5, linewidth=1.5)
    axis.axhline(1e-3, color=MUTED, linestyle="--", linewidth=1.5)
    log_axis(axis)
    axis.set_xlabel("Paso temporal (s)")
    axis.set_ylabel("Máxima variación relativa\nde la energía total")
    save(figure, "energia-paso")


def benchmark() -> None:
    rows = read_csv(RESULTS / "benchmark-summary.csv")
    figure, axis = plt.subplots(figsize=(7.0, 5.0))
    for engine, label, color, marker in (("tp3", "TP3: eventos", ORANGE, "s"), ("tp4", "TP4: paso temporal", BLUE, "o")):
        data = sorted((int(r["n"]), float(r["seconds_mean"]), float(r["seconds_std"]))
                      for r in rows if r["engine"] == engine)
        n, mean, std = map(np.array, zip(*data))
        axis.errorbar(n, mean, yerr=std, color=color, marker=marker, markersize=5, capsize=3, linewidth=1.5,
                      label=label)
    log_axis(axis, "y")
    axis.set_xlabel("Cantidad de partículas")
    axis.set_ylabel("Tiempo de ejecución (s)")
    axis.legend(loc="lower right")
    save(figure, "rendimiento")


def fraction_axis(axis, tf: float) -> None:
    axis.axhline(0.9, color=MUTED, linestyle="--", linewidth=1.5)
    axis.yaxis.set_major_locator(FixedLocator([0, 0.2, 0.4, 0.6, 0.8, 0.9, 1]))
    axis.set_xlim(0, tf)
    axis.set_ylim(0, 1.02)
    axis.set_xlabel("Tiempo (s)")
    axis.set_ylabel("Fracción de partículas usadas")


def mean_curves(npz, mask) -> tuple[np.ndarray, np.ndarray]:
    selected = npz["fu"][mask]
    return selected.mean(axis=0), selected.std(axis=0, ddof=1)


def position() -> None:
    fu = np.load(RESULTS / "position-fu.npz")
    times = fu["times"]
    positions = sorted(set(fu["x0"].tolist()))
    chosen = [positions[0], positions[len(positions) // 2], positions[-1]]
    figure, axis = plt.subplots(figsize=(7.2, 5.0))
    for x0, color, name in zip(chosen, (BLUE, ORANGE, AQUA), ("r", "R/2", "R − r")):
        mean, std = mean_curves(fu, (fu["n"] == 100) & (fu["x0"] == x0))
        axis.plot(times, mean, color=color, label=name)
        axis.fill_between(times, mean - std, mean + std, color=color, alpha=0.18, linewidth=0)
    fraction_axis(axis, times[-1])
    axis.legend(title="Posición $x_0$", loc="lower right", title_fontsize=18)
    save(figure, "posicion-fu")

    rows = read_csv(RESULTS / "position-summary.csv")
    figure, axis = plt.subplots(figsize=(7.0, 5.0))
    for n, color, marker in ((100, BLUE, "o"), (20, ORANGE, "s")):
        data = sorted((float(r["x0_m"]), number(r, "t90_mean_s"), number(r, "t90_std_s"))
                      for r in rows if int(r["n"]) == n)
        complete = [(x, m, s) for x, m, s in data if m is not None]
        x, mean, std = map(np.array, zip(*complete))
        axis.errorbar(x, mean, yerr=std, color=color, marker=marker, capsize=4, linewidth=1.5, label=f"N = {n}")
    axis.set_xlabel("Posición de los obstáculos $x_0$ (m)")
    axis.set_ylabel(r"$\langle t_{90}\rangle$ (s)")
    axis.set_ylim(bottom=0)
    axis.legend(loc="upper center")
    save(figure, "posicion-t90")


def speed_figures() -> None:
    summary = json.loads((RESULTS / "speed-summary.json").read_text())
    evolution = read_csv(RESULTS / "speed-evolution.csv")
    times = sorted({float(r["t_s"]) for r in evolution if float(r["t_s"]) > 0})
    figure, axis = plt.subplots(figsize=(7.2, 5.0))
    for index, t in enumerate(times):
        data = [(float(r["v_m_s"]), float(r["density_s_m"])) for r in evolution if float(r["t_s"]) == t]
        axis.step(*zip(*data), where="mid", color=BLUES(index / max(1, len(times) - 1)), linewidth=1.6,
                  label=f"{comma(t)} s")
    stationary = read_csv(RESULTS / "speed-stationary.csv")
    v = np.array([float(r["v_m_s"]) for r in stationary])
    density = np.array([float(r["density_mean_s_m"]) for r in stationary])
    axis.step(v, density, where="mid", color=ORANGE, linewidth=2.2, label="estacionario")
    axis.set_xlim(0, 3.0)
    axis.set_ylim(bottom=0)
    axis.set_xlabel("Rapidez (m/s)")
    axis.set_ylabel("Densidad de probabilidad (s/m)")
    axis.legend(title="Tiempo", loc="upper right", fontsize=17, title_fontsize=17)
    save(figure, "rapidez-evolucion")

    std = np.array([float(r["density_std_s_m"]) for r in stationary])
    kbt = summary["kbt_j"]
    figure, axis = plt.subplots(figsize=(6.4, 4.8))
    fine = np.linspace(0, 3.0, 400)
    axis.plot(fine, speed.maxwell_boltzmann(fine, 0.025, kbt), color=ORANGE, label="Ajuste")
    axis.errorbar(v, density, yerr=std, color=BLUE, marker="o", markersize=6, linestyle="none", capsize=3,
                  label="Simulación")
    axis.set_xlim(0, 3.0)
    axis.set_ylim(bottom=0)
    axis.set_xlabel("Rapidez (m/s)")
    axis.set_ylabel("Densidad de probabilidad (s/m)")
    axis.legend(loc="upper right")
    save(figure, "rapidez-ajuste")

    error = read_csv(RESULTS / "speed-fit-error.csv")
    k = np.array([float(r["kbt_j"]) for r in error])
    e = np.array([float(r["error"]) for r in error])
    window = (k > 0.6 * kbt) & (k < 1.4 * kbt)
    figure, axis = plt.subplots(figsize=(6.4, 4.8))
    axis.plot(k[window] * 100, e[window], color=BLUE)
    axis.plot([kbt * 100], [np.interp(kbt, k, e)], color=ORANGE, marker="o", markersize=11, linestyle="none")
    axis.set_ylim(bottom=0)
    axis.set_xlabel("$k_BT$ ($10^{-2}$ J)")
    axis.set_ylabel("Error del ajuste (s²/m²)")
    save(figure, "rapidez-error")


def density() -> None:
    fu = np.load(RESULTS / "density-fu.npz")
    counts = sorted(set(fu["n"].tolist()))
    shown = [n for n in counts if n in (20, 200, 400, 550, 600, 650)]
    figure, axis = plt.subplots(figsize=(7.6, 5.0))
    for index, n in enumerate(shown):
        mean, std = mean_curves(fu, fu["n"] == n)
        color = BLUES(index / max(1, len(shown) - 1))
        axis.plot(fu["times"], mean, color=color, label=f"{n}")
        axis.fill_between(fu["times"], mean - std, mean + std, color=color, alpha=0.15, linewidth=0)
    fraction_axis(axis, fu["times"][-1])
    axis.legend(title="N", loc="upper left", bbox_to_anchor=(1.01, 1.0), title_fontsize=18)
    save(figure, "densidad-fu")

    rows = sorted(read_csv(RESULTS / "density-summary.csv"), key=lambda r: int(r["n"]))
    tf = fu["times"][-1]
    figure, axis = plt.subplots(figsize=(7.0, 5.4))
    for key, label, color, marker in (("t90", r"$\langle t_{90}\rangle$", BLUE, "o"),
                                      ("t100", r"$\langle t_{100}\rangle$", ORANGE, "s")):
        complete = [(int(r["n"]) / AREA, float(r[f"{key}_mean_s"]), float(r[f"{key}_std_s"]))
                    for r in rows if int(r[f"{key}_missing"]) == 0]
        x, mean, std = map(np.array, zip(*complete))
        axis.errorbar(x, mean, yerr=std, color=color, marker=marker, capsize=4, linewidth=1.5, label=label)
        # Sin media: alguna realización no llega antes de tf. Si no llega a 0,9 tampoco llega a 1,
        # así que para t100 solo se marcan los N donde todavía hay t90.
        censored = [int(r["n"]) / AREA for r in rows if int(r[f"{key}_missing"]) > 0
                    and (key == "t90" or int(r["t90_missing"]) == 0)]
        axis.plot(censored, [tf] * len(censored), color=color, marker=marker, markerfacecolor="white",
                  markeredgewidth=2, linestyle="none")
    axis.axhline(tf, color=MUTED, linestyle="--", linewidth=1.5)
    axis.plot([], [], color=MUTED, marker="o", markerfacecolor="white", markeredgewidth=2, linestyle="none",
              label="no llegan todas")
    axis.set_yscale("log")
    axis.yaxis.set_major_locator(FixedLocator([10, 20, 50, 100, 200, 300]))
    axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _: comma(value)))
    axis.yaxis.set_minor_formatter(NullFormatter())
    axis.set_ylim(10, 400)
    axis.set_xlim(0, 850)
    axis.set_xlabel("Densidad (partículas/m²)")
    axis.set_ylabel("Tiempo (s)")
    top = axis.secondary_xaxis("top", functions=(lambda rho: rho * AREA, lambda n: n / AREA))
    top.set_xticks([100, 200, 300, 400, 500, 600])
    top.set_xlabel("Cantidad de partículas", fontsize=18)
    top.tick_params(labelsize=16)
    handles, labels = axis.get_legend_handles_labels()
    order = sorted(range(len(labels)), key=lambda i: labels[i] == "no llegan todas")
    axis.legend([handles[i] for i in order], [labels[i] for i in order], loc="lower right", fontsize=16)
    save(figure, "densidad-tiempos")


def heatmap() -> None:
    rows = read_csv(RESULTS / "position-summary.csv") + read_csv(RESULTS / "map-summary.csv")
    counts = sorted({int(r["n"]) for r in rows})
    positions = sorted({float(r["x0_m"]) for r in rows})
    grid = np.full((len(counts), len(positions)), np.nan)
    for r in rows:
        grid[counts.index(int(r["n"])), positions.index(float(r["x0_m"]))] = number(r, "t90_mean_s") or np.nan
    figure, axis = plt.subplots(figsize=(8.0, 4.8))
    step = positions[1] - positions[0]
    image = axis.imshow(grid, origin="lower", aspect="auto", cmap=BLUES,
                        extent=(positions[0] - step / 2, positions[-1] + step / 2, -0.5, len(counts) - 0.5))
    for i, j in zip(*np.nonzero(np.isnan(grid))):
        axis.text(positions[j], i, "×", ha="center", va="center", fontsize=20, color=INK)
    for i, row in enumerate(grid):
        if np.isfinite(row).any():
            axis.plot(positions[int(np.nanargmin(row))], i, marker="o", markersize=13, markerfacecolor="none",
                      markeredgecolor=ORANGE, markeredgewidth=3, linestyle="none")
    axis.yaxis.set_major_locator(FixedLocator(range(len(counts))))
    axis.set_yticklabels([str(n) for n in counts])
    axis.grid(False)
    axis.set_xlabel("Posición de los obstáculos $x_0$ (m)")
    axis.set_ylabel("Cantidad de partículas")
    bar = figure.colorbar(image, ax=axis, pad=0.02)
    bar.set_label(r"$\langle t_{90}\rangle$ (s)")
    save(figure, "mapa-t90")


def tex_number(text: str) -> str:
    return text.replace(".", "{,}")


def tex_power(value: float) -> str:
    """2e-05 -> 2\\times10^{-5}; 1e-04 -> 10^{-4}."""
    exponent = int(np.floor(np.log10(value)))
    mantissa = round(value / 10**exponent, 6)
    if mantissa == 1:
        return f"10^{{{exponent}}}"
    return tex_number(f"{mantissa:g}") + rf"\times10^{{{exponent}}}"


def tex_measure(value: float, error: float, exponent: int | None = None) -> str:
    """Valor y error en modo matemático, con las cifras que permite el error [T00, p. 70]."""
    if exponent is None:
        exponent = int(np.floor(np.log10(abs(value))))
        if -1 <= exponent <= 2:
            exponent = 0
    shown, uncertainty = stats.significant(value / 10**exponent, error / 10**exponent)
    body = tex_number(shown) + r"\pm" + tex_number(uncertainty)
    return f"({body})" + rf"\times10^{{{exponent}}}" if exponent else body


def cpu_name(text: str) -> str:
    """'11th Gen Intel(R) Core(TM) i7-1165G7 @ 2.80GHz' -> 'Intel Core i7-1165G7'."""
    text = re.sub(r"\((R|TM)\)", "", text.split("@")[0])
    return " ".join(re.sub(r"^\d+\w* Gen ", "", text.strip()).split())


def position_text(rows: list[dict]) -> str:
    """Mínimo de cada N y posiciones cuya media está a menos de un desvío de él."""
    lines = [r"\textbf{Menor $\langle t_{90}\rangle$}"]
    for n in (100, 20):
        group = sorted((float(r["x0_m"]), float(r["t90_mean_s"]), float(r["t90_std_s"]))
                       for r in rows if int(r["n"]) == n)
        x_best, mean_best, std_best = min(group, key=lambda g: g[1])
        close = [x for x, mean, _ in group if mean - mean_best <= std_best]
        lines.append(rf"$N={n}$: $x_0={tex_number(f'{x_best:.2f}')}$ m")
        lines.append(rf"\quad ${tex_measure(mean_best, std_best)}$ s")
        lines.append(rf"\quad a menos de $1\sigma$: {tex_number(f'{min(close):.2f}')} a {tex_number(f'{max(close):.2f}')} m")
    return r"\\".join(lines)


def map_text(rows: list[dict]) -> str:
    missing = sum(int(r["t90_missing"]) for r in rows)
    lines = [r"Círculo: mínimo de cada $N$"]
    for n in sorted({int(r["n"]) for r in rows}):
        best = min((r for r in rows if int(r["n"]) == n), key=lambda r: float(r["t90_mean_s"]))
        lines.append(rf"$N={n}$: ${tex_measure(float(best['t90_mean_s']), float(best['t90_std_s']))}$ s")
    if missing:
        lines.append(f"{missing} realizaciones no llegan a $F_{{\\mathrm u}}=0{{,}}9$")
    return r"\\".join(lines)


def density_text(runs: list[dict]) -> str:
    """Para cada umbral, los N en los que alguna realización no llega antes de tf:
    cuántas no llegan y su Fu(tf) (media y desvío entre esas realizaciones) [TP04, p. 3]."""
    blocks = []
    for key, level in (("t100", "1"), ("t90", "0{,}9")):
        rows = []
        for n in sorted({int(r["n"]) for r in runs}):
            group = [r for r in runs if int(r["n"]) == n]
            # Si no llega a 0,9 tampoco llega a 1: esos N se informan solo con el umbral 0,9.
            if key == "t100" and any(number(r, "t90_s") is None for r in group):
                continue
            final = [float(r["fu_final"]) for r in group if number(r, f"{key}_s") is None]
            if not final:
                continue
            mean, std = stats.mean_and_std(final)
            value = tex_measure(mean, std, 0) if len(final) > 1 else tex_number(f"{mean:.3f}")
            rows.append(rf"{n} & {len(final)}/{len(group)} & ${value}$\\")
        if rows:
            blocks.append(rf"\multicolumn{{3}}{{@{{}}l}}{{\textbf{{No llegan a $\fu={level}$}}}}\\" + "".join(rows))
    header = r"$N$ & no llegan & su $\fu(t_f)$\\"
    return (r"{\footnotesize\setlength{\tabcolsep}{3pt}\begin{tabular}{@{}rcc@{}}" + header
            + r"[2pt]".join(blocks) + r"\end{tabular}}")


def values() -> None:
    """Macros con los números de la presentación, calculadas desde los resultados."""
    macros = {"pasoElegido": tex_power(DT), "rapidezRealizaciones": "?", "tEstacionario": "?",
              "deltaEElegido": "?", "cpu": "?", "desvioRendimiento": "?", "kbtAjuste": "?",
              "posicionTexto": "", "mapaTexto": "", "densidadTexto": ""}
    if (RESULTS / "energy-summary.csv").exists():
        row = next(r for r in read_csv(RESULTS / "energy-summary.csv") if np.isclose(float(r["dt_s"]), DT))
        macros["deltaEElegido"] = tex_measure(float(row["delta_e_mean"]), float(row["delta_e_std"]))
    if (RESULTS / "speed-summary.json").exists():
        s = json.loads((RESULTS / "speed-summary.json").read_text())
        macros["rapidezRealizaciones"] = str(s["realizations"])
        macros["tEstacionario"] = tex_number(f"{s['stationary_start_s']:g}")
        macros["kbtAjuste"] = tex_measure(s["kbt_j"], s["kbt_per_realization_std_j"], -2)
    if (RESULTS / "benchmark-summary.csv").exists():
        machine = json.loads((RESULTS / "benchmark-machine.json").read_text())
        macros["cpu"] = cpu_name(machine["cpu"])
        spread = max(float(r["seconds_std"]) / float(r["seconds_mean"]) for r in read_csv(RESULTS / "benchmark-summary.csv"))
        macros["desvioRendimiento"] = tex_number(f"{100 * spread:.1f}")
    if (RESULTS / "position-summary.csv").exists():
        macros["posicionTexto"] = position_text(read_csv(RESULTS / "position-summary.csv"))
    if (RESULTS / "density-runs.csv").exists():
        macros["densidadTexto"] = density_text(read_csv(RESULTS / "density-runs.csv"))
    if (RESULTS / "map-summary.csv").exists():
        macros["mapaTexto"] = map_text(read_csv(RESULTS / "position-summary.csv") + read_csv(RESULTS / "map-summary.csv"))
    lines = [rf"\newcommand{{\{name}}}{{{value}}}" for name, value in macros.items()]
    (ROOT / "presentacion/valores.tex").write_text("\n".join(lines) + "\n")
    print("valores.tex")


def main() -> None:
    for build, required in ((oscillator, "oscillator-ecm.csv"), (energy, "energy-summary.csv"),
                            (benchmark, "benchmark-summary.csv"), (position, "position-summary.csv"),
                            (speed_figures, "speed-summary.json"), (density, "density-summary.csv"),
                            (heatmap, "map-summary.csv")):
        if (RESULTS / required).exists():
            build()
        else:
            print(f"sin datos para {build.__name__}: falta {required}")
    values()


if __name__ == "__main__":
    main()
