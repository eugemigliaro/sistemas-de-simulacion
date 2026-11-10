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

from common import DT, FIGURES, RAW, RESULTS, ROOT, T_STAR
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


def number(value: float, decimals: int = 0) -> str:
    """Número para LaTeX con coma decimal."""
    return f"{value:.{decimals}f}".replace(".", "{,}")


def pm(mean: float, std: float, decimals: int = 0) -> str:
    return f"{number(mean, decimals)}\\pm{number(std, decimals)}"


def rows(name: str) -> list[dict]:
    path = RESULTS / name
    if not path.exists():
        print(f"falta {name}: se omite su figura")
        return []
    with open(path) as fh:
        return list(csv.DictReader(fh))


def collision_rule() -> None:
    data = rows("collision-rule.csv")
    if not data:
        return
    figure, axis = plt.subplots(figsize=(7.4, 5.2))
    vn = np.linspace(0, 2.0, 200)
    axis.plot(vn, np.exp(-2 * KT * vn / KN), color=style.INK, linewidth=1.8, label=r"disco duro: $e^{-2\kappa v_n/k}$")
    for offset, color, marker in (("0.2", style.BLUE, "o"), ("0.5", style.ORANGE, "s"), ("0.8", style.AQUA, "^")):
        sel = [r for r in data if r["offset"] == offset]
        v = np.array([float(r["speed"]) for r in sel]) * math.sqrt(1 - float(offset) ** 2)
        axis.plot(v, [float(r["tangential_ratio"]) for r in sel], linestyle="none", marker=marker, color=color,
                  label=f"SFM blando, b = {offset.replace('.', ',')} σ")
    axis.set_xlabel(r"Velocidad normal $v_n$ (m/s)")
    axis.set_ylabel(r"$v_t$ después / $v_t$ antes")
    axis.set_xlim(0, 2.0)
    axis.set_ylim(0, 1)
    style.comma_axis(axis)
    axis.legend(loc="upper right", fontsize=16)
    style.save(figure, FIGURES / "regla-choque")


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


def clogs() -> None:
    data = rows("atascos.csv")
    if not data:
        return
    base = next(r for r in data if float(r["noise"]) == 0)
    VALUES["atascosSinFluctuacion"] = f"{base['clogged']} de {base['runs']}"
    VALUES["tevacSinFluctuacion"] = pm(float(base["t_evac_mean"]), float(base["t_evac_std"]))


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
    figure, (left, right) = plt.subplots(1, 2, figsize=(10.4, 5.4), gridspec_kw={"wspace": 0.45,
                                                                               "width_ratios": [2, 3]})
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
            lines.append(f"{name}: ${pm(float(r['t_evac_mean']), float(r['t_evac_std']))}$ s, "
                         f"se traban {r['clogged']} de {r['runs']}")
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
            VALUES["costoRelativoEDMD"] = number(cost["edmd"] / cost["tsdmd"])


def hybrid_fractions() -> None:
    per_run = [r for r in rows("poblacion-corridas.csv") if r["scheme"] == "hybrid"]
    if not per_run:
        return
    from tp5analysis.io import read_run
    from tp5analysis.observables import exit_times

    isolated = steps = agent_time = violations = top = 0.0
    for r in per_run:
        run = read_run(ROOT / "experiments" / "raw" / "poblacion" / f"hybrid_seed{r['seed']}.txt")
        isolated += run.summary["isolated_unrelaxed_steps"]
        violations += run.summary["bound_violations"]
        top = max(top, run.summary["max_speed"])
        steps += run.summary["agent_steps"]
        inside = np.concatenate([exit_times(run), np.full(run.agents - len(run.exits), run.summary["end_time"])])
        agent_time += inside.sum()
    VALUES["aisladosSinRelajar"] = f"el {number(100 * isolated / steps, 2)}\\,\\%"
    VALUES["fraccionTSDMD"] = f"el {number(100 * steps * DT / agent_time, 1)}\\,\\%"
    VALUES["rapidezMaxima"] = f"{number(top, 2)}~m/s"
    VALUES["violacionesCota"] = "ninguna" if violations == 0 else str(int(violations))


def _reference(axis, row: dict | None, column: str, scale: float, color: str, label: str) -> None:
    """Línea horizontal (media) y banda (desvío) de un esquema puro como referencia."""
    if row is None or not np.isfinite(float(row[f"{column}_mean"] or "nan")):
        return
    mean, std = scale * float(row[f"{column}_mean"]), scale * float(row[f"{column}_std"] or 0)
    axis.axhspan(mean - std, mean + std, color=color, alpha=0.15, linewidth=0)
    axis.axhline(mean, color=color, linewidth=2, linestyle="--", label=label)


def timing_tstar() -> None:
    official = (RESULTS / "tiempos-c.csv").exists()
    data = rows("tiempos-c.csv" if official else "tstar.csv")
    if not data:
        return
    hybrid = [r for r in data if r["t_star"] != ""]
    pure = {r["scheme"]: r for r in data if r["t_star"] == ""}
    t_star = np.array([float(r["t_star"]) for r in hybrid])
    figure, (left, right) = plt.subplots(1, 2, figsize=(12.0, 5.2), gridspec_kw={"wspace": 0.35})
    for axis, column, scale, label in ((left, "wall_finished", 1.0, "Tiempo de ejecución (s)"),
                                       (right, "cost_per_s", 1e3, "Costo (ms por s simulado)")):
        mean = np.array([scale * float(r[f"{column}_mean"]) for r in hybrid])
        std = np.array([scale * float(r[f"{column}_std"]) for r in hybrid])
        _reference(axis, pure.get("tsdmd"), column, scale, style.STEP, "TSDMD")
        if axis is right:  # en el izquierdo EDMD aplasta la escala; su valor va en el texto
            _reference(axis, pure.get("edmd"), column, scale, style.EVENT, "EDMD")
        ok = np.isfinite(mean)
        axis.errorbar(t_star[ok], mean[ok], yerr=std[ok], color=style.AQUA, marker="o", capsize=6,
                      linestyle="none", label="Híbrido")
        axis.set_xscale("log")
        axis.set_xlim(t_star.min() / 1.6, t_star.max() * 1.6)
        axis.set_xlabel("T* (s)")
        axis.set_ylabel(label)
        axis.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    right.set_yscale("log")
    right.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    left.set_title("corridas que terminan", fontsize=17, color=style.MUTED)
    right.set_title("todas las corridas", fontsize=17, color=style.MUTED)
    right.legend(loc="center right", fontsize=15)
    style.save(figure, FIGURES / "tiempos-tstar")

    figure, axis = plt.subplots(figsize=(7.6, 5.2))
    mean = np.array([float(r["t_evac_mean"]) for r in hybrid])
    std = np.array([float(r["t_evac_std"]) for r in hybrid])
    _reference(axis, pure.get("tsdmd"), "t_evac", 1.0, style.STEP, "TSDMD")
    ok = np.isfinite(mean)
    axis.errorbar(t_star[ok], mean[ok], yerr=std[ok], color=style.AQUA, marker="o", capsize=6, linestyle="none",
                  label="Híbrido")
    axis.set_xscale("log")
    axis.set_xlim(t_star.min() / 1.6, t_star.max() * 1.6)
    low, high = axis.get_ylim()
    axis.set_ylim(low - 0.08 * (high - low), high)
    for x, r in zip(t_star, hybrid):
        axis.annotate(f"{int(r['runs']) - int(r['clogged'])}/{r['runs']}", (x, axis.get_ylim()[0]),
                      textcoords="offset points", xytext=(0, 6), ha="center", fontsize=13, color=style.MUTED)
    axis.annotate("terminan:", (t_star.min() / 1.6, axis.get_ylim()[0]), textcoords="offset points",
                  xytext=(4, 24), fontsize=13, color=style.MUTED)
    axis.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    axis.set_xlabel("T* (s)")
    axis.set_ylabel("Tiempo de evacuación (s)")
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=15)
    style.save(figure, FIGURES / "tevac-tstar")
    if official:
        import json

        info = json.loads((RESULTS / "maquina.json").read_text())
        model = next((line.split(":", 1)[1].strip() for line in info.get("lscpu", "").splitlines()
                      if line.startswith("Model name")), info.get("sysctl") or info.get("processor") or "?")
        compiler = info.get("g++", "").splitlines()[0] if info.get("g++") else "?"
        compiler = compiler.replace(" version", "").split(" (")[0]
        VALUES["maquina"] = f"{model}, {compiler} con -O3; {info.get('workers', '?')} corridas a la vez"
        if "edmd" in pure and "tsdmd" in pure:
            edmd, tsdmd = float(pure["edmd"]["cost_per_s_mean"]), float(pure["tsdmd"]["cost_per_s_mean"])
            VALUES["costoEDMD"] = number(1e3 * edmd)
            VALUES["costoTSDMD"] = number(1e3 * tsdmd, 1)
            VALUES["costoRelativoEDMD"] = number(edmd / tsdmd, 1 if edmd / tsdmd < 10 else 0)
        walls = [float(r["wall_finished_mean"]) for r in data if r["wall_finished_mean"] not in ("", "nan")]
        hybrid_walls = [float(r["wall_finished_mean"]) for r in hybrid]
        done = [int(r["finished"]) for r in data if r["scheme"] != "edmd"]
        VALUES["terminanc"] = f"{min(done)} a {max(done)} de {data[0]['runs']}"
        if "tsdmd" in pure:
            reference = float(pure["tsdmd"]["wall_finished_mean"])
            VALUES["tiempoTSDMDc"] = pm(reference, float(pure["tsdmd"]["wall_finished_std"]), 1)
            VALUES["rangoHibridoc"] = f"{number(min(hybrid_walls), 2)} a {number(max(hybrid_walls), 2)}"
            std = float(pure["tsdmd"]["wall_finished_std"])
            inside = all(abs(float(r["wall_finished_mean"]) - reference) <= std + float(r["wall_finished_std"])
                         for r in hybrid if r["wall_finished_mean"] not in ("", "nan"))
            VALUES["textoTiemposc"] = (f"Híbrido: {VALUES['rangoHibridoc']} s; TSDMD: ${pm(reference, std, 2)}$ s"
                                       + (": todo dentro de las barras" if inside else ""))
            if "edmd" in pure and pure["edmd"]["wall_finished_mean"] not in ("", "nan"):
                e = pure["edmd"]
                VALUES["textoTiemposc"] += (f"; EDMD: ${pm(float(e['wall_finished_mean']), float(e['wall_finished_std']), 2)}$ s "
                                            f"({e['finished']} terminan)")
            tevac = [r for r in hybrid if r["t_evac_mean"] not in ("", "nan")]
            ref_t, ref_s = float(pure["tsdmd"]["t_evac_mean"]), float(pure["tsdmd"]["t_evac_std"])
            same_t = all(abs(float(r["t_evac_mean"]) - ref_t) <= ref_s + float(r["t_evac_std"]) for r in tevac)
            VALUES["textoTevacc"] = ("Así es: todos los $\\tstar$ quedan dentro de las barras de TSDMD" if same_t
                                     else "Hay $\\tstar$ que se apartan de TSDMD por fuera de las barras")
        paired = {r["config"]: r for r in rows("tiempos-c-pareado.csv")}
        if "tstar1" in paired:
            r = paired["tstar1"]
            VALUES["sobrecostoHibrido"] = (f"{number(100 * (float(r['cost_ratio_mean']) - 1), 1)}\\,\\%")
            VALUES["mismasSalidas"] = f"{r['same_exits']} de {r['pairs']}"
        small = [r for r in paired.values() if r["t_star"] not in ("", None) and float(r["t_star"]) <= 0.2]
        if small:
            ratios = [float(r["cost_ratio_mean"]) for r in small]
            spreads = [float(r["cost_ratio_std"]) for r in small]
            VALUES["rangoPareado"] = f"{number(min(ratios), 2)} a {number(max(ratios), 2)}"
            VALUES["textoPareado"] = (f"En promedio, {number(100 * (1 - np.mean(ratios)), 1)}\\,\\% más barato que TSDMD; "
                                      f"desvío entre semillas de {number(100 * min(spreads))} a {number(100 * max(spreads))}\\,\\%")
            best = min(small, key=lambda r: float(r["cost_ratio_std"]))
            n = int(best["pairs"])
            VALUES["mejorPareado"] = (f"$\\tstar={best['t_star'].replace('.', '{,}')}$ s: "
                                      f"${pm(float(best['cost_ratio_mean']), float(best['cost_ratio_std']), 3)}$ "
                                      f"(error estándar {number(float(best['cost_ratio_std']) / n ** 0.5, 3)})")
    else:
        VALUES["maquina"] = "preliminar: esta computadora, 7 corridas a la vez y 5 realizaciones"


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
            axis.set_xticks([100, 200, 400, 600, 1000])
            axis.set_xticklabels(["100", "200", "400", "600", "1000"])
            axis.minorticks_off()
            axis.set_xlabel("Agentes N")
            axis.set_title(title, fontsize=17, color=style.MUTED)
        axes[0].set_ylabel(label)
        axes[0].legend(loc="upper left", fontsize=15)
        if column == "wall_finished":
            axes[1].annotate("hueco: termina una sola corrida", (1, 0), xycoords="axes fraction", xytext=(-6, 8),
                             textcoords="offset points", ha="right", fontsize=13, color=style.MUTED)
        style.save(figure, FIGURES / name)


def recovery() -> None:
    """Recuperación de v_d con N = 200: costo por segundo simulado en la ventana inicial (con la
    relajación analítica, que no termina) y fracción de trabadas de las corridas completas."""
    full = rows("recuperacion.csv")
    window = rows("recuperacion-ventana.csv")
    if not full or not window:
        return
    from tp5analysis.stats import clopper_pearson

    figure, (left, right) = plt.subplots(1, 2, figsize=(12.0, 5.2), gridspec_kw={"wspace": 0.35})
    win = {r["variant"]: r for r in window}
    kicks = sorted((r for r in window if r["variant"].startswith("kicks")), key=lambda r: float(r["variant"][5:]))
    delta = np.array([float(r["variant"][5:]) for r in kicks])
    cost = np.array([1e3 * float(r["cost_per_s_mean"]) for r in kicks])
    err = np.array([1e3 * float(r["cost_per_s_std"]) for r in kicks])
    for key, color, label in (("tsdmd", style.STEP, "TSDMD"), ("hybrid", style.AQUA, "Híbrido"),
                              ("analytic0.01", style.PURPLE, "EDMD analítica (0,01 rad)")):
        if key in win:
            _reference(left, win[key], "cost_per_s", 1e3, color, label)
    left.errorbar(delta, cost, yerr=err, color=style.EVENT, marker="o", capsize=5, label="EDMD con patadas")
    left.set_yscale("log")
    left.set_ylabel("Costo (ms por s simulado)")
    left.set_title(f"primeros {number(float(window[0]['window']))} s simulados", fontsize=17, color=style.MUTED)
    left.legend(loc="center right", fontsize=13)
    by = {r["variant"]: r for r in full}
    kicks_full = sorted((r for r in full if r["kind"] == "kicks"), key=lambda r: float(r["value"]))
    d_full = np.array([float(r["value"]) for r in kicks_full])
    k = np.array([int(r["clogged"]) for r in kicks_full])
    n = np.array([int(r["runs"]) for r in kicks_full])
    ci = np.array([clopper_pearson(int(a), int(b)) for a, b in zip(k, n)])
    p_clog = 100 * k / n
    for key, color, label in (("tsdmd", style.STEP, "TSDMD"), ("hybrid", style.AQUA, "Híbrido")):
        if key in by:
            low, high = clopper_pearson(int(by[key]["clogged"]), int(by[key]["runs"]))
            right.axhspan(100 * low, 100 * high, color=color, alpha=0.15, linewidth=0)
            right.axhline(100 * int(by[key]["clogged"]) / int(by[key]["runs"]), color=color, linestyle="--",
                          linewidth=2, label=label)
    right.errorbar(d_full, p_clog, yerr=[p_clog - 100 * ci[:, 0], 100 * ci[:, 1] - p_clog], color=style.EVENT,
                   marker="o", capsize=5, linestyle="none", label="EDMD con patadas")
    right.set_ylim(0, 105)
    right.set_ylabel("Corridas trabadas (%)")
    right.set_title("corridas completas", fontsize=17, color=style.MUTED)
    right.legend(loc="lower left", fontsize=13)
    for axis in (left, right):
        axis.set_xscale("log")
        axis.set_xticks(delta)
        axis.set_xticklabels([f"{x:g}".replace(".", ",") for x in delta])
        axis.minorticks_off()
        axis.set_xlabel("δ entre patadas (s)")
    style.save(figure, FIGURES / "recuperacion")
    if "analytic0.01" in win and "kicks0.05" in win and "tsdmd" in win:
        an = float(win["analytic0.01"]["cost_per_s_mean"])
        VALUES["costoAnalitica"] = number(an, 0)
        VALUES["analiticaSobrePatadas"] = number(an / float(win["kicks0.05"]["cost_per_s_mean"]))
        VALUES["analiticaSobreTSDMD"] = number(an / float(win["tsdmd"]["cost_per_s_mean"]))
        VALUES["trabadasPatadas"] = f"{k.min()} a {k.max()} de {n.max()}"
        VALUES["textoRecuperacion"] = (
            f"\\begin{{puntos}}\\item Analítica: {number(an, 0)} s por s simulado, {VALUES['analiticaSobrePatadas']} "
            f"veces las patadas ($\\delta=0{{,}}05$ s); no termina\\item Patadas: se traban {k.min()} a {k.max()} "
            f"de {n.max()}, como EDMD puro con la regla original\\end{{puntos}}")


def texts() -> None:
    """Frases con números para las diapositivas (estudios con N = 200)."""
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
    if "edmd" in summary:
        ed = summary["edmd"]
        VALUES["atascosEDMD"] = f"{ed['clogged']} de {ed['runs']}"
    if "tsdmd" in summary:
        VALUES["atascosTSDMD"] = f"{summary['tsdmd']['clogged']} de {summary['tsdmd']['runs']}"
        VALUES["textoEDMDCurvas"] = f"se traba en {ed['clogged']} de {ed['runs']}, casi siempre al principio"
    if {"edmd_nucleo", "edmd", "tsdmd"} <= summary.keys():
        nu, ed, ts = summary["edmd_nucleo"], summary["edmd"], summary["tsdmd"]
        VALUES["textoNucleo"] = (f"Se traban {nu['clogged']} de {nu['runs']} (IC {pct(nu['p_low'])}--{pct(nu['p_high'])}\\,\\%), "
                                 f"contra {ed['clogged']} con la regla original y {ts['clogged']} con TSDMD: "
                                 + ("no se acerca a TSDMD" if not overlap(nu, ts) else "se acerca a TSDMD"))
    compression = rows("compresion.csv")
    if compression:
        VALUES["xiMedio"] = number(100 * float(compression[0]["xi_mean"]), 2)
    stiff = sorted((RAW / "exploracion").glob("kn*_seed*.txt"))
    if stiff:
        from tp5analysis.io import read_run

        runs = [read_run(path) for path in stiff]
        exits = [len(r.exits) for r in runs]
        clogged = sum(1 for r in runs if not r.finished)
        VALUES["textoPruebaK"] = (f"$k$ diez veces mayor (menos compresión): {clogged} de {len(runs)} semillas que "
                                  f"evacuaban se traban al principio (salen {min(exits)} a {max(exits)} de {runs[0].agents})")
    fluct = rows("atascos.csv")
    if fluct:
        counts = ", ".join(f"{r['clogged']}" for r in fluct[:-1]) + f" y {fluct[-1]['clogged']}"
        amps = ", ".join(pct(r["noise"]) for r in fluct[:-1]) + f" y {pct(fluct[-1]['noise'])}"
        same = all(overlap(fluct[0], r) for r in fluct[1:])
        VALUES["textoFluctuacion"] = (f"Trabadas: {counts} de {fluct[0]['runs']} con {amps}\\,\\%"
                                      + ("; intervalos superpuestos: sin efecto significativo" if same else ""))
    target = rows("segundo_target.csv")
    if target:
        chosen = next(r for r in target if r["chosen"] == "1")
        VALUES["textoSegundoTarget"] = ("Todas las opciones se superponen con alejarse: el cuello de botella está adentro"
                                        if chosen["option"] == "away" else f"La mejor opción es {chosen['option']}")


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
    import build_consulta

    for name, function in (("atascos", build_consulta.population_curves),
                           ("atascos.csv", build_consulta.clog_probability),
                           ("animaciones/tsdmd_seed401.txt", build_consulta.compression)):
        if (RAW / name).exists() or (RESULTS / name).exists():
            function(FIGURES)
    collision_rule()
    collision_dt()
    dt_flow()
    second_target()
    clogs()
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
    cost_conclusion()
    write_values()


if __name__ == "__main__":
    main()
