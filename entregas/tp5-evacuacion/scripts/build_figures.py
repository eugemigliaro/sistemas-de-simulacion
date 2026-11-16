"""Figuras de la presentación a partir de experiments/results [GPRES, pp. 1-2]: ejes en
palabras con unidades, sin títulos, tipografía grande y puntos con símbolo. Cada figura se
omite si faltan sus datos. También escribe presentacion/valores.tex con los números que
cita la presentación (solo los que ya tienen datos).

Uso: python scripts/build_figures.py
"""
from __future__ import annotations

import csv
import math

import numpy as np

from common import AGENTS, DT, FIGURES, HYBRID_OPTIONS, RAW, RESULTS, ROOT, T_STAR, T_STARS
from tp5analysis import style

import matplotlib.pyplot as plt  # noqa: E402

KN, KT = 1.2e5, 2.4e5
SCHEME_STYLE = {  # color, marcador y nombre de cada esquema
    "tsdmd": (style.STEP, "s", "TSDMD"),
    "hybrid": (style.AQUA, "o", "Híbrido"),
    "edmd": (style.EVENT, "^", "EDMD"),
    "edmd_nucleo": (style.PURPLE, "D", "EDMD, núcleo reducido"),
}
MAIN = ("tsdmd", "hybrid", "edmd")  # esquemas del cuerpo; edmd_nucleo va al apéndice
VALUES: dict[str, str] = {}


def relative(ratio: float) -> str:
    """Costo de un esquema relativo a TSDMD, en palabras: "7,6 veces" o "1/140"."""
    if ratio >= 1:
        return f"{number(ratio, 1 if ratio < 10 else 0)} veces el de TSDMD"
    return f"1/{number(1 / ratio)} del de TSDMD"


def duration(seconds: float, std: float | None = None) -> str:
    """Tiempo de ejecución con unidades legibles (ms si es menor a 1 s)."""
    scale, unit, decimals = (1e3, "ms", 1 if seconds < 0.01 else 0) if seconds < 1 else (1.0, "s", 2)
    if std is None:
        return f"{number(scale * seconds, decimals)} {unit}"
    return f"${pm(scale * seconds, scale * std, decimals)}$ {unit}"


def number(value: float, decimals: int = 0) -> str:
    """Número para LaTeX con coma decimal."""
    return f"{value:.{decimals}f}".replace(".", "{,}")


def pm(mean: float, std: float, decimals: int = 0) -> str:
    return f"{number(mean, decimals)}\\pm{number(std, decimals)}"


N200_RAW = RAW / "n200"          # apéndice: atascos con N = 200, como contraste
N200_RESULTS = RESULTS / "n200"


def rows_at(folder, name: str) -> list[dict]:
    path = folder / name
    if not path.exists():
        print(f"falta {path.relative_to(ROOT)}: se omite")
        return []
    with open(path) as fh:
        return list(csv.DictReader(fh))


def rows(name: str) -> list[dict]:
    path = RESULTS / name
    if not path.exists():
        print(f"falta {name}: se omite su figura")
        return []
    with open(path) as fh:
        return list(csv.DictReader(fh))


def collision_rule() -> None:
    """Gráfico de paridad: velocidad del agente i después de un choque aislado según la regla de
    disco duro (x) y según el SFM blando (y), componentes x e y, para cada rapidez y parámetro de
    impacto. Si la regla reproduce el SFM, los puntos caen sobre la recta y = x."""
    data = rows("collision-rule.csv")
    if not data or "velocity_i_x" not in data[0]:
        return
    figure, axis = plt.subplots(figsize=(7.0, 6.2))
    values = [float(r[k]) for r in data for k in ("velocity_i_x", "velocity_i_y", "hard_velocity_i_x", "hard_velocity_i_y")]
    margin = 0.08 * (max(values) - min(values))
    low, high = min(values) - margin, max(values) + margin
    axis.plot([low, high], [low, high], color=style.INK, linewidth=1.5, zorder=1, label="y = x")
    colors = {"0.2": style.BLUE, "0.5": style.ORANGE, "0.8": style.AQUA}
    for offset, color in colors.items():
        sel = [r for r in data if r["offset"] == offset]
        for component, marker in (("x", "o"), ("y", "s")):
            axis.plot([float(r[f"hard_velocity_i_{component}"]) for r in sel],
                      [float(r[f"velocity_i_{component}"]) for r in sel], linestyle="none", marker=marker,
                      color=color, markersize=8, zorder=2)
    for offset, color in colors.items():
        axis.plot([], [], linestyle="none", marker="o", color=color, label=f"b = {offset.replace('.', ',')} σ")
    axis.plot([], [], linestyle="none", marker="o", color=style.MUTED, markerfacecolor="white", label="componente x")
    axis.plot([], [], linestyle="none", marker="s", color=style.MUTED, markerfacecolor="white", label="componente y")
    axis.set_xlim(low, high)
    axis.set_ylim(low, high)
    axis.set_aspect("equal")
    axis.set_xticks([-0.25, 0, 0.25, 0.5, 0.75, 1])
    axis.set_yticks([-0.25, 0, 0.25, 0.5, 0.75, 1])
    axis.set_xlabel("Regla de disco duro (m/s)")
    axis.set_ylabel("SFM blando (m/s)")
    style.comma_axis(axis)
    axis.legend(loc="upper left", fontsize=15)
    style.save(figure, FIGURES / "regla-choque")
    errors = [math.hypot(float(r["velocity_i_x"]) - float(r["hard_velocity_i_x"]),
                         float(r["velocity_i_y"]) - float(r["hard_velocity_i_y"])) / float(r["speed"]) for r in data]
    VALUES["errorReglaMax"] = f"{number(100 * max(errors), 1)}\\,\\%"
    frontal = [e for e, r in zip(errors, data) if r["offset"] == "0.2"]
    VALUES["errorReglaFrontal"] = f"{number(100 * max(frontal), 1)}\\,\\%"


def collision_dt() -> None:
    data = rows("collision-dt.csv")
    if not data:
        return
    dt = np.array([float(r["dt"]) for r in data])
    error = np.abs(np.abs(np.array([float(r["normal_ratio"]) for r in data])) - 1)
    figure, axis = plt.subplots(figsize=(7.0, 5.0))
    axis.loglog(dt * 1e3, error * 100, marker="o", color=style.BLUE)
    axis.axvline(2, color=style.MUTED, linestyle="--", linewidth=1.5)
    axis.set_xlabel("Paso temporal dt (ms)")
    axis.set_ylabel("Error en la restitución normal (%)")
    style.save(figure, FIGURES / "dt-choque")


def dt_flow() -> None:
    data = rows("dt.csv")
    if not data:
        return
    dt = np.array([float(r["dt"]) for r in data]) * 1e3
    mean = np.array([float(r["flow_mean"]) for r in data])
    std = np.array([float(r["flow_std"]) for r in data])
    figure, axis = plt.subplots(figsize=(6.8, 5.0))
    axis.errorbar(dt, mean, yerr=std, color=style.BLUE, marker="o", capsize=6, linestyle="none")
    axis.set_xscale("log")
    axis.set_xticks(dt)
    axis.set_xticklabels([f"{x:g}".replace(".", ",") for x in dt])
    axis.minorticks_off()
    axis.set_xlabel("Paso temporal dt (ms)")
    axis.set_ylabel("Caudal J (agentes/s)")
    axis.set_ylim(0.35, 0.6)
    style.comma_axis(axis, "y")
    style.save(figure, FIGURES / "dt-caudal")


def second_target() -> None:
    data = rows("segundo_target.csv")
    if not data:
        return
    points = [r for r in data if r["option"] != "away"]
    away = next(r for r in data if r["option"] == "away")
    d = np.array([float(r["distance"]) for r in points])
    mean = np.array([float(r["t_evac_mean"]) for r in points])
    std = np.array([float(r["t_evac_std"]) for r in points])
    figure, axis = plt.subplots(figsize=(7.2, 5.0))
    am, asd = float(away["t_evac_mean"]), float(away["t_evac_std"])
    axis.axhspan(am - asd, am + asd, color=style.ORANGE, alpha=0.15, linewidth=0)
    axis.axhline(am, color=style.ORANGE, linewidth=2, label="alejarse (−y)")
    axis.errorbar(d, mean, yerr=std, color=style.BLUE, marker="o", capsize=6, linestyle="none",
                  label="punto común (L/2, −D)")
    axis.set_xscale("log")
    axis.set_xticks([1.25, 2, 5, 10, 20])
    axis.set_xticklabels(["1,25", "2", "5", "10", "20"])
    axis.minorticks_off()
    axis.set_xlabel("Distancia D del segundo target (m)")
    axis.set_ylabel("Tiempo de evacuación (s)")
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=16, handletextpad=0.4)
    style.save(figure, FIGURES / "segundo-target")


def population_data() -> dict | None:
    path = RESULTS / "poblacion-curvas.npz"
    if not path.exists():
        print("falta poblacion-curvas.npz: se omiten las figuras de a y b")
        return None
    with np.load(path) as data:
        return {k: data[k] for k in data.files}


def scheme_fractions(data: dict) -> None:
    if "hybrid_event" not in data:
        return
    t = data["mode_times"]
    figure, axis = plt.subplots(figsize=(7.6, 5.2))
    for key, color, label in (("hybrid_event", style.EVENT, "EDMD"), ("hybrid_step", style.STEP, "TSDMD")):
        values = data[key]
        mean, std = values.mean(axis=0), values.std(axis=0, ddof=1)
        axis.fill_between(t, mean - std, mean + std, color=color, alpha=0.2, linewidth=0)
        axis.plot(t, mean, color=color, label=label)
    axis.set_xlabel("Tiempo (s)")
    axis.set_ylabel("Agentes adentro")
    agents = float((data["hybrid_event"][:, 0] + data["hybrid_step"][:, 0]).max())
    axis.set_xlim(0, t[-1])
    axis.set_ylim(0, 1.02 * agents)
    axis.legend(loc="center right")
    style.save(figure, FIGURES / "fraccion-esquemas")
    mean_event = data["hybrid_event"].mean(axis=0)
    gone = t[np.argmax(mean_event < 1)] if np.any(mean_event < 1) else float("nan")
    VALUES["tiempoVueloLibre"] = f"unos {number(5 * round(gone / 5))} s"
    VALUES["realizacionesPoblacion"] = str(len(data["hybrid_event"]))


def population_curves(data: dict) -> None:
    times = data["times"]
    figure, axis = plt.subplots(figsize=(8.4, 5.4))
    for scheme, (color, marker, label) in SCHEME_STYLE.items():
        if f"{scheme}_curves" not in data or scheme not in MAIN:
            continue
        curves, finished = data[f"{scheme}_curves"], data[f"{scheme}_finished"]
        if finished.sum() >= 2:
            done = np.nan_to_num(curves[finished], nan=0.0)  # las que terminan quedan en 0
            mean, std = done.mean(axis=0), done.std(axis=0, ddof=1)
            axis.fill_between(times, mean - std, mean + std, color=color, alpha=0.18, linewidth=0)
            axis.plot(times, mean, color=color, label=f"{label} ({finished.sum()} terminan)")
        else:
            axis.plot([], [], color=color, linestyle="--", label=f"{label} ({finished.sum()} terminan)")
        for curve in curves[~finished]:
            valid = np.isfinite(curve)
            axis.plot(times[valid], curve[valid], color=color, linewidth=1.0, alpha=0.55, linestyle="--")
            axis.plot(times[valid][-1], curve[valid][-1], marker="x", color=color, markersize=7, markeredgewidth=1.6)
    axis.plot([], [], color=style.MUTED, linewidth=1.0, linestyle="--", marker="x", markersize=7,
              label="se traba (una corrida)")
    axis.set_xlabel("Tiempo (s)")
    axis.set_ylabel("Agentes adentro")
    ends = [np.max(np.where(np.isfinite(c))[0]) for k in SCHEME_STYLE if f"{k}_curves" in data
            for c in data[f"{k}_curves"]]
    axis.set_xlim(0, times[max(ends)] * 1.02 if ends else times[-1])
    axis.set_ylim(0, 1.02 * float(np.nanmax([data[f"{k}_curves"][:, 0].max() for k in SCHEME_STYLE
                                               if f"{k}_curves" in data])))
    axis.legend(loc="lower left", fontsize=16)
    style.save(figure, FIGURES / "poblacion-esquemas")


def evacuation_by_scheme() -> None:
    summary = [r for r in rows("poblacion.csv") if r["scheme"] in MAIN]
    per_run = [r for r in rows("poblacion-corridas.csv") if r["scheme"] in MAIN]
    if not summary:
        return
    figure, (left, right) = plt.subplots(1, 2, figsize=(11.0, 5.4), gridspec_kw={"wspace": 0.45,
                                                                               "width_ratios": [1, 1]})
    names = [r["scheme"] for r in summary]
    done = [r["scheme"] for r in summary if int(r["finished"]) >= 2]
    for k, r in enumerate(summary):
        color, marker, _ = SCHEME_STYLE[r["scheme"]]
        p, low, high = (100 * float(r[c]) for c in ("p_clog", "p_low", "p_high"))
        right.errorbar(k, p, yerr=[[p - low], [high - p]], color=color, marker=marker, capsize=8, markersize=11,
                       linestyle="none")
        right.annotate(f"{r['clogged']}/{r['runs']}", (k, p), textcoords="offset points", xytext=(12, -5),
                       fontsize=16, color=style.MUTED)
        if r["scheme"] not in done:
            continue
        k = done.index(r["scheme"])
        values = [float(p["t_evac"]) for p in per_run if p["scheme"] == r["scheme"] and p["finished"] == "1"]
        jitter = np.linspace(-0.18, 0.18, len(values)) if len(values) > 1 else np.zeros(len(values))
        left.plot(k + jitter, values, linestyle="none", marker=marker, color=color, alpha=0.35, markersize=6)
        left.errorbar(k, float(r["t_evac_mean"]), yerr=float(r["t_evac_std"]), color=style.INK, marker=marker,
                      markerfacecolor=color, capsize=8, markersize=11, linestyle="none")
    for axis, keys in ((left, done), (right, names)):
        axis.set_xticks(np.arange(len(keys)))
        axis.set_xticklabels([SCHEME_STYLE[n][2] for n in keys])
        axis.set_xlim(-0.6, len(keys) - 0.4)
        axis.grid(axis="x", visible=False)
    left.set_ylabel("Tiempo de evacuación (s)")
    right.set_ylabel("Corridas trabadas (%)")
    right.set_ylim(0, 105)
    style.save(figure, FIGURES / "tevac-esquemas")
    lines = []
    for r in summary:
        name = SCHEME_STYLE[r["scheme"]][2]
        if int(r["finished"]) >= 2:
            lines.append(f"{name}: ${pm(float(r['t_evac_mean']), float(r['t_evac_std']))}$ s")
        else:
            lines.append(f"{name}: se traban {r['clogged']} de {r['runs']}")
    VALUES["textoEvacuacion"] = "\\\\".join(lines)
    edmd = [p for p in per_run if p["scheme"] == "edmd"]
    if edmd:
        exited = [int(p["exited"]) for p in edmd if p["finished"] == "0"] or [0]  # las trabadas
        VALUES["salidasEDMD"] = f"entre {min(exited)} y {max(exited)}"
        cost = {r["scheme"]: float(r["cost_per_s_mean"]) for r in summary}
        VALUES["costoEDMD"] = number(1e3 * cost["edmd"])  # timing_tstar lo reemplaza con el punto c
        if "tsdmd" in cost:
            VALUES["costoTSDMD"] = number(1e3 * cost["tsdmd"], 1)
            VALUES["costoRelativoEDMD"] = relative(cost["edmd"] / cost["tsdmd"])


def hybrid_fractions() -> None:
    per_run = [r for r in rows("poblacion-corridas.csv") if r["scheme"] == "hybrid"]
    if not per_run:
        return
    from tp5analysis.io import read_run
    from tp5analysis.observables import exit_times

    isolated = steps = agent_time = violations = top = 0.0
    busy = []  # fracción de pasos con algún agente TSDMD
    for r in per_run:
        run = read_run(ROOT / "experiments" / "raw" / "poblacion" / f"hybrid_seed{r['seed']}.txt")
        isolated += run.summary["isolated_unrelaxed_steps"]
        violations += run.summary["bound_violations"]
        top = max(top, run.summary["max_speed"])
        steps += run.summary["agent_steps"]
        inside = np.concatenate([exit_times(run), np.full(run.agents - len(run.exits), run.summary["end_time"])])
        agent_time += inside.sum()
        from tp5analysis.observables import mode_counts

        grid = np.arange(0.0, float(run.summary["end_time"]), DT)
        busy.append(float((mode_counts(run, grid)[1] > 0).mean()))
    VALUES["aisladosSinRelajar"] = f"el {number(100 * isolated / steps, 2)}\\,\\%"
    VALUES["fraccionTSDMD"] = f"el {number(100 * steps * DT / agent_time, 1)}\\,\\%"
    VALUES["rapidezMaxima"] = f"{number(top, 2)}~m/s"
    VALUES["pasosConTSDMD"] = f"el {number(100 * float(np.mean(busy)))}\\,\\%"
    switched = [len({int(i) for t, i, m in read_run(ROOT / "experiments" / "raw" / "poblacion" / f"hybrid_seed{r['seed']}.txt").modes
                     if m == 0 and t > 0}) for r in per_run]
    VALUES["agentesAlgunaVezTSDMD"] = f"el {number(100 * np.mean(switched) / AGENTS)}\\,\\%"
    back = [sum(1 for t, i, m in read_run(ROOT / "experiments" / "raw" / "poblacion" / f"hybrid_seed{r['seed']}.txt").modes
                if m == 1 and t > 0) for r in per_run]
    VALUES["vueltasEDMD"] = number(float(np.mean(back)), 0 if np.mean(back) >= 1 else 2)
    VALUES["vueltasEDMDtotal"] = f"{sum(back)} en {len(back)} corridas"
    VALUES["violacionesCota"] = "ninguna" if violations == 0 else str(int(violations))


def _reference(axis, row: dict | None, column: str, scale: float, color: str, label: str) -> None:
    """Línea horizontal (media) y banda (desvío) de un esquema puro como referencia."""
    if row is None or not np.isfinite(float(row[f"{column}_mean"] or "nan")):
        return
    mean, std = scale * float(row[f"{column}_mean"]), scale * float(row[f"{column}_std"] or 0)
    axis.axhspan(mean - std, mean + std, color=color, alpha=0.15, linewidth=0)
    axis.axhline(mean, color=color, linewidth=2, linestyle="--", label=label)


def timing_tstar() -> None:
    """Punto c: tiempo de ejecución y t_evac en función de T* para las dos variantes del
    híbrido (relajación analítica y recuperación por el SFM; la principal, en lleno, es la de
    HYBRID_OPTIONS), con TSDMD y EDMD puros de referencia; valores del pareado por semilla."""
    data = rows("tiempos-c.csv")
    if not data:
        return
    main = "analitica" if HYBRID_OPTIONS.get("relaxation") == "analytic" else "sfm"
    variants = {"analitica": (style.AQUA, "o", "Híbrido, relajación analítica"),
                "sfm": (style.PURPLE, "D", "Híbrido, relaja el SFM")}
    pure = {r["scheme"]: r for r in data if r["t_star"] == ""}
    by_variant = {v: [r for r in data if r.get("variant") == v] for v in variants}
    every = [float(r["t_star"]) for r in data if r["t_star"] != ""]
    figure, (left, right) = plt.subplots(1, 2, figsize=(12.0, 5.2), gridspec_kw={"wspace": 0.35})
    for axis, column, scale, label in ((left, "wall_finished", 1e3, "Tiempo de ejecución (ms)"),
                                       (right, "cost_per_s", 1e3, "Costo (ms por s simulado)")):
        _reference(axis, pure.get("tsdmd"), column, scale, style.STEP, "TSDMD")
        if axis is right:  # en el izquierdo EDMD aplasta la escala; su valor va en el texto
            _reference(axis, pure.get("edmd"), column, scale, style.EVENT, "EDMD")
        for variant, (color, marker, text) in variants.items():
            sel = by_variant[variant]
            if not sel:
                continue
            x = np.array([float(r["t_star"]) for r in sel])
            mean = np.array([scale * float(r[f"{column}_mean"]) for r in sel])
            std = np.array([scale * float(r[f"{column}_std"]) for r in sel])
            ok = np.isfinite(mean)
            axis.errorbar(x[ok], mean[ok], yerr=std[ok], color=color, marker=marker, capsize=5, linestyle="none",
                          label=text, markerfacecolor=color if variant == main else "white")
        axis.set_xscale("log")
        axis.set_xlim(min(every) / 1.6, max(every) * 1.6)
        axis.set_xlabel("T* (s)")
        axis.set_ylabel(label)
        axis.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    low, high = right.get_ylim()
    if high / max(low, 1e-12) > 10:  # EDMD muy por encima: escala logarítmica
        right.set_yscale("log")
    right.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    left.set_title("corridas que terminan", fontsize=17, color=style.MUTED)
    right.set_title("todas las corridas", fontsize=17, color=style.MUTED)
    handles, labels = right.get_legend_handles_labels()
    figure.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.98), ncol=4, fontsize=15)
    style.save(figure, FIGURES / "tiempos-tstar")

    figure, axis = plt.subplots(figsize=(7.6, 5.2))
    _reference(axis, pure.get("tsdmd"), "t_evac", 1.0, style.STEP, "TSDMD")
    for variant, (color, marker, text) in variants.items():
        sel = by_variant[variant]
        if not sel:
            continue
        x = np.array([float(r["t_star"]) for r in sel]) * (1.08 if variant != main else 1.0)
        mean = np.array([float(r["t_evac_mean"]) for r in sel])
        std = np.array([float(r["t_evac_std"]) for r in sel])
        ok = np.isfinite(mean)
        axis.errorbar(x[ok], mean[ok], yerr=std[ok], color=color, marker=marker, capsize=5, linestyle="none",
                      label=text, markerfacecolor=color if variant == main else "white")
    axis.set_xscale("log")
    axis.set_xlim(min(every) / 1.6, max(every) * 1.6)
    axis.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    axis.set_xlabel("T* (s)")
    axis.set_ylabel("Tiempo de evacuación (s)")
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=13)
    style.save(figure, FIGURES / "tevac-tstar")

    import json

    info = json.loads((RESULTS / "maquina.json").read_text())
    model = next((line.split(":", 1)[1].strip() for line in info.get("lscpu", "").splitlines()
                  if line.startswith("Model name")), info.get("sysctl") or info.get("processor") or "?")
    model = model.replace("11th Gen Intel(R) Core(TM) ", "Intel Core ").replace(" @ 2.80GHz", "")
    first = info.get("g++", "").splitlines()[0] if info.get("g++") else "?"
    # "g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0" -> "g++ 15.2.0"; "Apple clang version 21.0.0 (...)" -> "Apple clang 21.0.0"
    compiler = (f"g++ {first.split()[-1]}" if first.startswith("g++")
                else first.replace(" version", "").split(" (")[0])
    VALUES["maquina"] = f"{model}, {compiler} con -O3; {info.get('workers', '?')} corridas a la vez"
    if "edmd" in pure and "tsdmd" in pure:
        edmd, tsdmd = float(pure["edmd"]["cost_per_s_mean"]), float(pure["tsdmd"]["cost_per_s_mean"])
        VALUES["costoEDMD"] = number(1e3 * edmd, 2)
        VALUES["costoTSDMD"] = number(1e3 * tsdmd, 1)
        VALUES["costoRelativoEDMD"] = relative(edmd / tsdmd)
    done = [int(r["finished"]) for r in data if r["scheme"] != "edmd"]
    VALUES["terminanc"] = f"{min(done)} a {max(done)} de {data[0]['runs']}"
    if "tsdmd" in pure:
        reference, std = float(pure["tsdmd"]["wall_finished_mean"]), float(pure["tsdmd"]["wall_finished_std"])
        parts = []
        for variant, (_, _, text) in variants.items():
            walls = [float(r["wall_finished_mean"]) for r in by_variant[variant]]
            if walls:
                parts.append(f"{text.replace('Híbrido, ', '')}: {duration(min(walls))} a {duration(max(walls))}")
        VALUES["textoTiemposc"] = "Híbrido " + "; ".join(parts) + f"; TSDMD: {duration(reference, std)}"
        costs = []
        for variant, (_, _, text) in variants.items():
            values = [1e3 * float(r["cost_per_s_mean"]) for r in by_variant[variant]]
            if values:
                costs.append(f"{text.replace('Híbrido, ', '').replace('relajación ', '')} {number(min(values), 2)} a {number(max(values), 2)}")
        ts_cost = pure["tsdmd"]
        line = (f"Costo (ms por s simulado): " + "; ".join(costs)
                + f"; TSDMD ${pm(1e3 * float(ts_cost['cost_per_s_mean']), 1e3 * float(ts_cost['cost_per_s_std']), 2)}$")
        if "edmd" in pure:
            e = pure["edmd"]
            line += f"; EDMD ${pm(1e3 * float(e['cost_per_s_mean']), 1e3 * float(e['cost_per_s_std']), 2)}$"
        VALUES["textoCostoc"] = line
        if "edmd" in pure and pure["edmd"]["wall_finished_mean"] not in ("", "nan"):
            e = pure["edmd"]
            VALUES["textoTiemposc"] += f"; EDMD: {duration(float(e['wall_finished_mean']), float(e['wall_finished_std']))}"
        ref_t, ref_s = float(pure["tsdmd"]["t_evac_mean"]), float(pure["tsdmd"]["t_evac_std"])
        tevac = [r for v in variants for r in by_variant[v] if r["t_evac_mean"] not in ("", "nan")]
        same_t = all(abs(float(r["t_evac_mean"]) - ref_t) <= ref_s + float(r["t_evac_std"]) for r in tevac)
        VALUES["textoTevacc"] = ("Así es: las dos variantes, con todos los $\\tstar$, quedan dentro de las barras de TSDMD"
                                 if same_t else "Hay $\\tstar$ que se apartan de TSDMD por fuera de las barras")
    paired = [r for r in rows("tiempos-c-pareado.csv") if r.get("variant")]
    for variant, key in (("analitica", "Analitica"), ("sfm", "SFM")):
        sel = [r for r in paired if r["variant"] == variant]
        at = next((r for r in sel if abs(float(r["t_star"]) - T_STAR) < 1e-12), None)
        if at:
            n = int(at["pairs"])
            VALUES[f"costoHibrido{key}"] = number(float(at["cost_ratio_mean"]), 2)
            VALUES[f"pareado{key}"] = (f"${pm(float(at['cost_ratio_mean']), float(at['cost_ratio_std']), 2)}$ "
                                       f"(error estándar {number(float(at['cost_ratio_std']) / n ** 0.5, 2)})")
        if sel:
            ratios = [float(r["cost_ratio_mean"]) for r in sel]
            VALUES[f"rangoPareado{key}"] = f"{number(min(ratios), 2)} a {number(max(ratios), 2)}"
    from tp5analysis.io import read_run

    folder = RAW / "tiempos" / f"base{AGENTS}" / "c"
    isolated = steps = 0.0
    for path in sorted(folder.glob(f"hybrid_tstar{T_STAR:g}_seed*.txt")):
        run = read_run(path)
        isolated += run.summary.get("isolated_unrelaxed_steps", 0.0)
        steps += run.summary.get("agent_steps", 0.0)
    if steps:
        VALUES["aisladosSinRelajarSFM"] = f"el {number(100 * isolated / steps)}\\,\\%"
    # Costo por segundo simulado sobre el del TSDMD de la misma semilla, solo en los pares en
    # que terminan los dos: el costo por segundo de una corrida trabada depende de cuántos
    # quedan adentro, así que un atasco en uno solo rompe el pareo (decisiones del 2026-11-16).
    def cost(run) -> float:
        return float(run.summary["wall_seconds"]) / float(run.summary["end_time"])

    def load(pattern: str) -> dict:
        return {path.stem.split("seed")[1]: read_run(path) for path in folder.glob(pattern)}

    tsdmd = load("tsdmd_seed*.txt")

    def finished_ratios(runs: dict) -> list[float]:
        both = [s for s in runs if s in tsdmd and runs[s].finished and tsdmd[s].finished]
        return [cost(runs[s]) / cost(tsdmd[s]) for s in both]

    for prefix, key in (("hybridan", "Analitica"), ("hybrid", "SFM"), ("edmd", "EDMD")):
        runs = load(f"{prefix}_tstar{T_STAR:g}_seed*.txt" if prefix != "edmd" else "edmd_seed*.txt")
        if not runs:
            continue
        ratios = finished_ratios(runs)
        if len(ratios) >= 2:
            mean, std = float(np.mean(ratios)), float(np.std(ratios, ddof=1))
            VALUES[f"pareadoTerminan{key}"] = f"${pm(mean, std, 2)}$ ({len(ratios)} pares)"
            VALUES[f"costoTerminan{key}"] = number(mean, 2)
            if key == "EDMD":
                VALUES["costoRelativoEDMD"] = relative(mean)
        if prefix == "edmd":
            continue
        VALUES[f"cambios{key}"] = number(float(np.mean([r.summary["switches"] for r in runs.values()])))
        VALUES[f"eventos{key}"] = number(float(np.mean([r.summary["events"] for r in runs.values()])))
        means = [float(np.mean(r)) for r in (finished_ratios(load(f"{prefix}_tstar{s:g}_seed*.txt")) for s in T_STARS) if r]
        if means:
            VALUES[f"rangoTerminan{key}"] = f"{number(min(means), 2)} a {number(max(means), 2)}"


def timing_scaling() -> None:
    data = rows("tiempos-d.csv")
    if not data:
        return
    for column, scale, label, name in (("wall_finished", 1.0, "Tiempo de ejecución (s)", "escalamiento-wall"),
                                       ("cost_per_s", 1e3, "Costo (ms por s simulado)", "escalamiento-costo")):
        figure, axes = plt.subplots(1, 2, figsize=(12.0, 5.2), sharey=True, gridspec_kw={"wspace": 0.12})
        for axis, variant, title in zip(axes, ("densidad", "sala"), ("densidad inicial constante", "L = 50 m")):
            for scheme, (color, marker, text) in SCHEME_STYLE.items():
                sel = [r for r in data if r["variant"] == variant and r["scheme"] == scheme]
                n = np.array([int(r["agents"]) for r in sel])
                mean = np.array([scale * float(r[f"{column}_mean"]) for r in sel])
                std = np.array([scale * float(r[f"{column}_std"]) for r in sel])
                ok = np.isfinite(mean)
                if ok.any():
                    axis.errorbar(n[ok], mean[ok], yerr=std[ok], color=color, marker=marker, capsize=5, label=text)
                    count = np.array([int(r["finished"]) if column == "wall_finished" else int(r["runs"])
                                      for r in sel])
                    single = ok & (count == 1)
                    axis.plot(n[single], mean[single], linestyle="none", marker=marker, color=color,
                              markerfacecolor="white", markersize=10, markeredgewidth=2, zorder=5)
                    if column == "cost_per_s" and ok.sum() >= 3:
                        slope = np.polyfit(np.log(n[ok]), np.log(mean[ok]), 1)[0]
                        VALUES[f"exponente{variant.capitalize()}{text.replace('í', 'i')}"] = number(slope, 1)
            axis.set_xscale("log")
            axis.set_yscale("log")
            ticks = sorted({int(r["agents"]) for r in data})
            axis.set_xticks(ticks)
            axis.set_xticklabels([str(n) for n in ticks])
            axis.minorticks_off()
            axis.set_xlabel("Agentes N")
            axis.set_title(title, fontsize=17, color=style.MUTED)
        axes[0].set_ylabel(label)
        axes[0].legend(loc="upper left", fontsize=15)
        if column == "cost_per_s":
            dens = {(r["scheme"], int(r["agents"])): float(r["cost_per_s_mean"]) for r in data if r["variant"] == "densidad"}
            counts = sorted({n for _, n in dens})
            for n, key in ((counts[0], "hibridoSobreTSDMDchico"), (counts[-1], "hibridoSobreTSDMDgrande")):
                if ("hybrid", n) in dens and ("tsdmd", n) in dens:
                    VALUES[key] = number(dens[("hybrid", n)] / dens[("tsdmd", n)], 2)
        if column == "wall_finished":
            axes[1].annotate("hueco: termina una sola corrida", (1, 0), xycoords="axes fraction", xytext=(-6, 8),
                             textcoords="offset points", ha="right", fontsize=13, color=style.MUTED)
        style.save(figure, FIGURES / name)


def recovery() -> None:
    """Recuperación de v_d: diferencia de caudal con el TSDMD de la misma semilla contra el costo
    por segundo simulado de cada variante (patadas con varios delta y relajación analítica con
    varias tolerancias; TSDMD y el híbrido como referencias)."""
    data = rows("recuperacion.csv")
    if not data:
        return
    figure, axis = plt.subplots(figsize=(8.6, 5.4))
    axis.axhline(0, color=style.STEP, linewidth=2, linestyle="--")
    kinds = {"kicks": (style.EVENT, "o", "EDMD con patadas (δ en s)"),
             "analytic": (style.PURPLE, "D", "EDMD analítica (tolerancia en rad)"),
             "hybrid": (style.AQUA, "o", "Híbrido"), "tsdmd": (style.STEP, "s", "TSDMD")}
    for kind, (color, marker, label) in kinds.items():
        sel = [r for r in data if r["kind"] == kind and r["flow_diff_mean"] not in ("", "nan")]
        if not sel:
            continue
        x = np.array([1e3 * float(r["cost_per_s_mean"]) for r in sel])
        y = np.array([float(r["flow_diff_mean"]) for r in sel])
        e = np.array([float(r["flow_diff_std"]) for r in sel])
        axis.errorbar(x, y, yerr=e, color=color, marker=marker, capsize=5, linestyle="none", label=label)
        if kind in ("kicks", "analytic"):
            for xi, yi, r in zip(x, y, sel):
                axis.annotate(f"{float(r['value']):g}".replace(".", ","), (xi, yi), textcoords="offset points",
                              xytext=(6, 6), fontsize=13, color=color)
    axis.set_xscale("log")
    axis.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    axis.set_xlabel("Costo (ms por s simulado)")
    axis.set_ylabel("J − J$_{TSDMD}$ (agentes/s)")
    style.comma_axis(axis, "y")
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=13)
    style.save(figure, FIGURES / "recuperacion")
    by = {r["variant"]: r for r in data}
    kicks = [r for r in data if r["kind"] == "kicks"]
    analytic = [r for r in data if r["kind"] == "analytic"]
    if kicks and analytic and "kicks0.05" in by:
        cost = lambda r: float(r["cost_per_s_mean"])
        reference = cost(by["kicks0.05"])
        clogged = sum(int(r["clogged"]) for r in data)
        within = all(abs(float(r["flow_diff_mean"])) <= float(r["flow_diff_std"]) for r in kicks + analytic
                     if r["flow_diff_mean"] not in ("", "nan"))
        VALUES["textoRecuperacion"] = (
            "\\begin{puntos}"
            + ("\\item Patadas y analítica: el mismo caudal que TSDMD, dentro de las barras" if within else "")
            + f"\\item Analítica: {number(min(map(cost, analytic)) / reference, 1)} a "
              f"{number(max(map(cost, analytic)) / reference, 1)} veces el costo de las patadas con $\\delta=0{{,}}05$ s"
            + (f"\\item Ninguna corrida se traba" if clogged == 0 else f"\\item Se traban {clogged} corridas en total")
            + "\\end{puntos}")


def texts() -> None:
    """Frases con números para las diapositivas: el cuerpo con N = AGENTS, el apéndice de
    atascos con N = AGENTS (arco, rigidez y fricción) y, como contraste, con N = 200."""
    def pct(x) -> str:
        return number(100 * float(x))

    def overlap(a: dict, b: dict) -> bool:
        return float(a["p_low"]) <= float(b["p_high"]) and float(b["p_low"]) <= float(a["p_high"])

    summary = {r["scheme"]: r for r in rows("poblacion.csv")}
    if {"tsdmd", "hybrid"} <= summary.keys():
        ts, hy = summary["tsdmd"], summary["hybrid"]
        same_clog = overlap(ts, hy)
        same_t = abs(float(ts["t_evac_mean"]) - float(hy["t_evac_mean"])) <= float(ts["t_evac_std"]) + float(hy["t_evac_std"])
        VALUES["textoComparacion"] = ("Híbrido: mismo $t_{\\rm evac}$ y misma fracción de trabadas que TSDMD, dentro de las barras"
                                      if same_clog and same_t else "Híbrido: difiere de TSDMD por fuera de las barras")
    for scheme, key in (("tsdmd", "atascosTSDMD"), ("hybrid", "atascosHibrido"), ("edmd", "atascosEDMD")):
        if scheme in summary:
            r = summary[scheme]
            VALUES[key] = f"{r['clogged']} de {r['runs']}"
            VALUES[key + "IC"] = f"{r['clogged']} de {r['runs']} (IC {pct(r['p_low'])}--{pct(r['p_high'])}\\,\\%)"
    if set(MAIN) <= summary.keys():
        same = overlap(summary["tsdmd"], summary["edmd"]) and overlap(summary["tsdmd"], summary["hybrid"])
        VALUES["textoAtascos"] = ("Trabadas: intervalos superpuestos, los tres se traban igual" if same
                                  else "Trabadas: hay intervalos que no se superponen")
    if {"tsdmd", "edmd"} <= summary.keys():
        ts, ed = summary["tsdmd"], summary["edmd"]
        same_t = abs(float(ts["t_evac_mean"]) - float(ed["t_evac_mean"])) <= float(ts["t_evac_std"]) + float(ed["t_evac_std"])
        VALUES["textoEDMDCurvas"] = (f"se traba en {ed['clogged']} de {ed['runs']}"
                                     + ("; misma evacuación que TSDMD dentro de las barras" if same_t and overlap(ts, ed) else ""))
    per_run = [r for r in rows("poblacion-corridas.csv") if r["scheme"] == "tsdmd" and r["finished"] == "0"]
    if per_run:
        left = [AGENTS - int(r["exited"]) for r in per_run]
        last = [float(r["last_exit"]) for r in per_run]
        VALUES["quedanTrabadas"] = f"{min(left)} a {max(left)}"
        VALUES["ultimaSalidaTrabadas"] = f"{number(min(last))} a {number(max(last))} s"
    # Apéndice: rigidez y fricción con N = AGENTS.
    stiff = {r["variant"]: r for r in rows("rigidez.csv")}
    for name, key in (("paper", "Paper"), ("k10", "Kdiez"), ("k10_kappa10", "KKappaDiez")):
        if name in stiff:
            r = stiff[name]
            VALUES[f"trabadas{key}"] = f"{r['clogged']} de {r['runs']} (IC {pct(r['p_low'])}--{pct(r['p_high'])}\\,\\%)"
            VALUES[f"tevac{key}"] = f"${pm(float(r['t_evac_mean']), float(r['t_evac_std']), 1)}$ s"
            if name != "paper":
                VALUES[f"diferencia{key}"] = f"${pm(float(r['dt_evac_mean']), float(r['dt_evac_std']), 1)}$ s"
    # Apéndice: contraste con N = 200.
    old = {r["scheme"]: r for r in rows_at(N200_RESULTS, "poblacion.csv")}
    for scheme, key in (("tsdmd", "atascosTSDMDdoscientos"), ("edmd", "atascosEDMDdoscientos")):
        if scheme in old:
            VALUES[key] = f"{old[scheme]['clogged']} de {old[scheme]['runs']}"
    if {"edmd_nucleo", "edmd", "tsdmd"} <= old.keys():
        nu, ed, ts = old["edmd_nucleo"], old["edmd"], old["tsdmd"]
        VALUES["textoNucleo"] = (f"Se traban {nu['clogged']} de {nu['runs']} (IC {pct(nu['p_low'])}--{pct(nu['p_high'])}\\,\\%), "
                                 f"contra {ed['clogged']} con la regla original y {ts['clogged']} con TSDMD: "
                                 + ("no se acerca a TSDMD" if not overlap(nu, ts) else "se acerca a TSDMD"))
    compression = rows_at(N200_RESULTS, "compresion.csv")
    if compression:
        VALUES["xiMedio"] = number(100 * float(compression[0]["xi_mean"]), 2)
    old_stiff = sorted((N200_RAW / "exploracion").glob("kn*_seed*.txt"))
    if old_stiff:
        from tp5analysis.io import read_run

        runs = [read_run(path) for path in old_stiff]
        exits = [len(r.exits) for r in runs]
        clogged = sum(1 for r in runs if not r.finished)
        VALUES["textoPruebaKdoscientos"] = (f"$k\\times10$: {clogged} de {len(runs)} semillas que evacuaban se traban "
                                            f"al principio (salen {min(exits)} a {max(exits)} de {runs[0].agents})")
    target = rows("segundo_target.csv")
    if target:
        chosen = next(r for r in target if r["chosen"] == "1")
        VALUES["textoSegundoTarget"] = ("Todas las opciones se superponen con alejarse: el cuello de botella está adentro"
                                        if chosen["option"] == "away" else f"La mejor opción es {chosen['option']}")


def contact_compression(path) -> tuple[list, list]:
    """Agentes adentro y superposición media (cm) de los contactos a menos de 1,5 m de la puerta."""
    from tp5analysis.io import iter_frames, read_run

    run = read_run(path)
    door = np.array([0.5 * float(run.params["side"]), 0.0])
    every = max(1, round(len(run.exits) / 6))  # unos 6 cuadros por salida
    inside, mean = [], []
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
            mean.append(100 * xi.mean())
    return inside, mean


def compression_contrast() -> None:
    """Apéndice: compresión de los contactos cerca de la puerta, N = AGENTS contra N = 200
    (TSDMD, semilla 401, una corrida que termina en cada caso)."""
    sources = ((RAW / "animaciones" / "tsdmd_seed401.txt", style.BLUE, "o", f"N = {AGENTS}"),
               (N200_RAW / "animaciones" / "tsdmd_seed401.txt", style.ORANGE, "s", "N = 200"))
    if not all(path.exists() for path, *_ in sources):
        print("faltan las animaciones de TSDMD para la compresión: se omite")
        return
    figure, axis = plt.subplots(figsize=(7.6, 5.2))
    means = {}
    for path, color, marker, label in sources:
        inside, mean = contact_compression(path)
        axis.plot(inside, mean, linestyle="none", marker=marker, markersize=5, color=color, label=label)
        means[label] = mean
    axis.set_xlabel("Agentes adentro")
    axis.set_ylabel("Superposición media ξ (cm)")
    axis.set_xlim(0, None)
    axis.set_ylim(0, None)
    style.comma_axis(axis, "y")
    axis.legend(loc="upper left")
    style.save(figure, FIGURES / "compresion")
    low = means[f"N = {AGENTS}"]
    VALUES["compresionN"] = f"{number(min(low), 1)} a {number(max(low), 1)} cm"
    high = means["N = 200"]
    VALUES["compresionDoscientos"] = f"hasta {number(max(high), 1)} cm"


def stiffness() -> None:
    """Apéndice: TSDMD con los parámetros del paper, con k diez veces mayor y con k y kappa
    diez veces mayores (mismas semillas): fracción de trabadas y t_evac de las que terminan."""
    data = rows("rigidez.csv")
    if not data:
        return
    labels = {"paper": "paper", "k10": "k×10", "k10_kappa10": "k, κ\n×10"}
    colors = {"paper": style.STEP, "k10": style.PURPLE, "k10_kappa10": style.AQUA}
    figure, (left, right) = plt.subplots(1, 2, figsize=(9.0, 5.2), gridspec_kw={"wspace": 0.45})
    for k, r in enumerate(data):
        color = colors[r["variant"]]
        p, low, high = (100 * float(r[c]) for c in ("p_clog", "p_low", "p_high"))
        left.errorbar(k, p, yerr=[[p - low], [high - p]], color=color, marker="o", capsize=8, markersize=11,
                      linestyle="none")
        left.annotate(f"{r['clogged']}/{r['runs']}", (k, p), textcoords="offset points", xytext=(12, -5),
                      fontsize=16, color=style.MUTED)
        right.errorbar(k, float(r["t_evac_mean"]), yerr=float(r["t_evac_std"]), color=color, marker="o",
                       capsize=8, markersize=11, linestyle="none")
    for axis in (left, right):
        axis.set_xticks(range(len(data)))
        axis.set_xticklabels([labels[r["variant"]] for r in data], fontsize=16)
        axis.set_xlim(-0.6, len(data) - 0.4)
        axis.grid(axis="x", visible=False)
    left.set_ylabel("Corridas trabadas (%)")
    left.set_ylim(0, 60)
    right.set_ylabel("Tiempo de evacuación (s)")
    right.set_ylim(0, None)
    style.save(figure, FIGURES / "rigidez")


def choose_n() -> None:
    """Apéndice: estudio para elegir N, costo del híbrido sobre el de TSDMD y sobre el de EDMD
    puro semilla por semilla, con barras de 3 errores estándar (el criterio)."""
    data = rows("elegir-n.csv")
    if not data:
        return
    n = np.array([int(r["agents"]) for r in data])
    figure, axis = plt.subplots(figsize=(8.4, 5.2))
    axis.axhline(1, color=style.MUTED, linewidth=1.5, linestyle="--")
    for other, color, marker, label, shift in (("tsdmd", style.STEP, "s", "híbrido / TSDMD", -0.8),
                                                 ("edmd", style.EVENT, "^", "híbrido / EDMD puro", 0.8)):
        mean = np.array([float(r[f"hybrid_over_{other}_mean"]) for r in data])
        se = np.array([float(r[f"hybrid_over_{other}_se"]) for r in data])
        axis.errorbar(n + shift, mean, yerr=3 * se, color=color, marker=marker, capsize=5, linestyle="none", label=label)
    chosen = [r for r in data if r["hybrid_best"] == "1"]
    for r in chosen:
        axis.axvspan(int(r["agents"]) - 4, int(r["agents"]) + 4, color=style.AQUA, alpha=0.15, linewidth=0)
    axis.set_yscale("log")
    axis.set_yticks([0.2, 0.5, 1, 2, 5])
    axis.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    axis.minorticks_off()
    axis.set_xticks(n)
    axis.set_xlabel("Agentes N (sala de 50 m)")
    axis.set_ylabel("Costo del híbrido / otro")
    axis.legend(loc="upper right", fontsize=15)
    style.save(figure, FIGURES / "elegir-n")
    if chosen:
        best = max(chosen, key=lambda r: float(r["margin"]))
        VALUES["nElegido"] = best["agents"]
        VALUES["textoElegirN"] = (
            f"Califica solo $N={best['agents']}$: sobre TSDMD {number(float(best['hybrid_over_tsdmd_mean']), 2)}, "
            f"sobre EDMD {number(float(best['hybrid_over_edmd_mean']), 2)}; margen {number(100 * float(best['margin']))}\\,\\%")
        VALUES["trabadasElegirN"] = (f"T {best['tsdmd_clogged']}, H {best['hybrid_clogged']}, E "
                                     f"{best['edmd_clogged']} de {best['pairs']}")
    cheapest = [int(r["agents"]) for r in data if float(r["hybrid_over_edmd_mean"]) > 1]
    if cheapest:
        VALUES["edmdMasBaratoHasta"] = str(max(cheapest))


def cost_conclusion() -> None:
    needed = ("textoPareado", "costoRelativoEDMD", "exponenteDensidadEDMD", "exponenteDensidadTSDMD")
    if all(k in VALUES for k in needed):
        saving = VALUES["textoPareado"].split(";")[0].replace("En promedio, ", "")
        VALUES["conclusionCosto"] = (f"Semilla por semilla: híbrido {saving}; EDMD puro, {VALUES['costoRelativoEDMD']} "
                                     f"veces más caro, y con densidad constante crece como $N^{{{VALUES['exponenteDensidadEDMD']}}}$ "
                                     f"(TSDMD, $N^{{{VALUES['exponenteDensidadTSDMD']}}}$)")


def write_values() -> None:
    VALUES.setdefault("dtElegido", number(DT * 1e3))
    VALUES.setdefault("tstarElegido", f"{T_STAR:g}".replace(".", "{,}"))
    path = ROOT / "presentacion" / "valores.tex"
    lines = [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in sorted(VALUES.items())]
    path.write_text("% Generado por scripts/build_figures.py: no editar a mano.\n" + "\n".join(lines) + "\n")
    print(f"{path.relative_to(ROOT)}: {len(lines)} valores")


def main() -> None:
    collision_rule()
    collision_dt()
    dt_flow()
    second_target()
    data = population_data()
    if data is not None:
        scheme_fractions(data)
        population_curves(data)
    evacuation_by_scheme()
    hybrid_fractions()
    timing_tstar()
    timing_scaling()
    recovery()
    texts()
    compression_contrast()
    stiffness()
    choose_n()
    cost_conclusion()
    write_values()


if __name__ == "__main__":
    main()
