#!/usr/bin/env python3
"""Barridos y animaciones de la sección Resultados de la presentación.

- ``disco``: un disco en el centro de la mesa con radio variable. Guarda t90
  por realización y la curva Fu(t) promedio de cada radio, para el mapa
  Fu(t, R).
- ``profundidad``: la superelipse adoptada con profundidad variable y el
  resto de los parámetros fijos.
- ``animaciones``: mesa vacía y configuración adoptada, en tiempo real, con
  Fu(t) debajo y t90 marcado.

Las trayectorias se borran después de extraer lo necesario; se regeneran con
la semilla.
"""

from __future__ import annotations

import argparse
import math
import statistics
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "python/src"))

import busqueda_elipses as be  # noqa: E402
from tp3analysis.goals import goal_curve, time_to_fraction  # noqa: E402
from tp3analysis.trajectory import read_trajectory  # noqa: E402

ENGINE = ROOT / "cpp/build/release/tp3"
RAW = ROOT / "experiments/raw/presentacion"
RESULTS = ROOT / "experiments/results/presentacion"
FIGURAS = ROOT / "presentacion/figuras"
VIDEOS = ROOT / "videos"

RADIOS = (0.05, 0.08, 0.11, 0.14, 0.17, 0.20, 0.23, 0.26, 0.29, 0.32, 0.34)
SEMILLAS_DISCO = range(12000, 12020)
TMAX_DISCO = 60.0
GRILLA_FU = np.round(np.arange(0.0, TMAX_DISCO + 1e-9, 0.1), 10)

PROFUNDIDADES = (0.17, 0.20, 0.23, 0.25, 0.277, 0.30, 0.33, 0.36, 0.40)
SEMILLAS_PROFUNDIDAD = range(13000, 13024)


def _config_disco(radio: float | None) -> tuple[str, str]:
    if radio is None:
        return "vacia", ""
    etiqueta = f"disco_r{radio * 100:02.0f}"
    ruta = RAW / "configs" / f"{etiqueta}.txt"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(f"0.60 0.34 {radio:.2f}\n", encoding="utf-8")
    return etiqueta, str(ruta.relative_to(ROOT))


def _correr_fu(trabajo: tuple[str, str, float, int]) -> dict[str, object]:
    etiqueta, ruta, radio, semilla = trabajo
    salida = RAW / "tray" / f"{etiqueta}_s{semilla}.txt"
    salida.parent.mkdir(parents=True, exist_ok=True)
    comando = [str(ENGINE), "simulate", "--n", "100", "--seed", str(semilla),
               "--tmax", str(TMAX_DISCO), "--save-every", "0", "--output", str(salida)]
    if ruta:
        comando += ["--config", str(ROOT / ruta)]
    subprocess.run(comando, check=True, capture_output=True, text=True)
    trayectoria = read_trajectory(salida)
    curva = goal_curve(trayectoria)
    resultado = time_to_fraction(trayectoria)
    salida.unlink()
    pasos = np.searchsorted(curva.times, GRILLA_FU, side="right") - 1
    return {
        "label": etiqueta, "radius_m": radio, "seed": semilla,
        "reached": int(resultado.reached),
        "t90_seconds": "" if resultado.t90 is None else resultado.t90,
        "goals_at_end": resultado.goals_at_end,
        "fu": curva.used_fraction[pasos],
    }


def etapa_disco() -> None:
    configs = [(*_config_disco(None), 0.0)]
    configs += [(*_config_disco(radio), radio) for radio in RADIOS]
    trabajos = [(etiqueta, ruta, radio, s) for etiqueta, ruta, radio in configs
                for s in SEMILLAS_DISCO]
    with ProcessPoolExecutor() as pool:
        filas = list(pool.map(_correr_fu, trabajos, chunksize=4))
    resumen, curvas = [], []
    for etiqueta, _, radio in configs:
        propias = [f for f in filas if f["label"] == etiqueta]
        t90 = [float(f["t90_seconds"]) for f in propias if f["reached"]]
        desvio = statistics.stdev(t90)
        resumen.append({
            "label": etiqueta, "radius_m": radio, "realizaciones": len(propias),
            "alcanzaron": len(t90), "mean_t90_seconds": statistics.fmean(t90),
            "std_t90_seconds": desvio, "sem_t90_seconds": desvio / math.sqrt(len(t90)),
        })
        media = np.mean([f["fu"] for f in propias], axis=0)
        curvas += [{"label": etiqueta, "radius_m": radio, "time_s": t, "mean_fu": fu}
                   for t, fu in zip(GRILLA_FU, media)]
    be.escribir(RESULTS / "t90_runs_disco.csv",
                [{k: v for k, v in f.items() if k != "fu"} for f in filas])
    be.escribir(RESULTS / "t90_summary_disco.csv", resumen)
    be.escribir(RESULTS / "fu_disco.csv", curvas)
    for fila in resumen:
        print(f"{fila['label']:12s} <t90> = {fila['mean_t90_seconds']:6.2f} ± "
              f"{fila['sem_t90_seconds']:.2f} s ({fila['alcanzaron']}/{fila['realizaciones']})")


def etapa_profundidad() -> None:
    elegida = be.ELEGIDA
    disenos = [be.DisenoSuper(p, elegida.semiancho, elegida.exponente, elegida.retroceso)
               for p in PROFUNDIDADES]
    configs = be.construir_todos(disenos)
    be.escribir(RESULTS / "plan_profundidad.csv", configs)
    filas = be.evaluar(configs, SEMILLAS_PROFUNDIDAD, 100.0, "profundidad")
    be.escribir(RESULTS / "t90_runs_profundidad.csv", filas)
    resumen = be.resumir(configs, filas)
    be.escribir(RESULTS / "t90_summary_profundidad.csv", resumen)
    for fila in resumen:
        print(f"P = {fila['profundidad_m']:.3f}  <t90> = {fila['mean_t90_seconds']:6.2f} ± "
              f"{fila['sem_t90_seconds']:.2f} s  errores = {fila['errores']}")


def _animacion(trabajo: tuple[str, str, int]) -> str:
    # El mismo punto de entrada que va en el ZIP de entrega: la cátedra pide
    # poder verificar que las animaciones no interpolan entre eventos.
    from tp3analysis.animar import animar

    etiqueta, ruta, semilla = trabajo
    salida = ROOT / "data/generated" / f"anim_goles_{etiqueta}.txt"
    salida.parent.mkdir(parents=True, exist_ok=True)
    comando = [str(ENGINE), "simulate", "--n", "100", "--seed", str(semilla), "--tmax", "30",
               "--save-every", "10", "--output", str(salida)]
    if ruta:
        comando += ["--config", str(ROOT / ruta)]
    subprocess.run(comando, check=True, capture_output=True, text=True)
    fin, t90 = animar(salida, VIDEOS / f"anim-goles-{etiqueta}.mp4",
                      FIGURAS / f"anim-goles-{etiqueta}.png")
    return f"{etiqueta}: semilla {semilla}, t90 = {t90:.2f} s, video de {fin:.0f} s"


def _semilla_representativa(tabla: Path, etiqueta: str) -> int:
    """La realización cuyo t90 queda más cerca de la media de su configuración."""
    filas = [f for f in be._leer(tabla) if f["label"] == etiqueta and f["reached"] == "1"]
    media = statistics.fmean(float(f["t90_seconds"]) for f in filas)
    return int(min(filas, key=lambda f: abs(float(f["t90_seconds"]) - media))["seed"])


def etapa_animaciones() -> None:
    trabajos = [
        ("vacia", "", _semilla_representativa(RESULTS / "t90_runs_disco.csv", "vacia")),
        ("elegida", str(be.FINAL_CONFIG.relative_to(ROOT)),
         _semilla_representativa(be.RESULTS / "t90_runs_desempate.csv", be.ELEGIDA.etiqueta)),
    ]
    with ProcessPoolExecutor() as pool:
        for linea in pool.map(_animacion, trabajos):
            print(linea)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("etapa", choices=("disco", "profundidad", "animaciones", "todo"))
    etapa = parser.parse_args().etapa
    etapas = {"disco": [etapa_disco], "profundidad": [etapa_profundidad],
              "animaciones": [etapa_animaciones],
              "todo": [etapa_disco, etapa_profundidad, etapa_animaciones]}[etapa]
    for funcion in etapas:
        funcion()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
