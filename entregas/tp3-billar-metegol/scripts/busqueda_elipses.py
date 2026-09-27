#!/usr/bin/env python3
"""Búsqueda de configuraciones con espejos elípticos hechos de discos.

Cada mitad de la mesa tiene una elipse cuyos focos son el centro de la mesa y
el centro de su arco. El contorno se arma con discos de radio ``rho`` (mínimo
``r``, por la restricción ii) ubicados sobre la curva paralela a la elipse, a
distancia ``rho + r``: así la superficie que ven los *centros* de las
partículas es la elipse buscada, independientemente de ``rho``.

Todo lo que queda fuera de las elipses se rellena con discos hasta que no
entre ninguna partícula. Sin ese relleno, las partículas generadas detrás del
espejo quedan encerradas sin arco y nunca hacen gol.

Variantes:
- cuello ``abierto``: la arena es la unión de las dos elipses; el foco común
  queda libre en el centro de la mesa.
- cuello ``cerrado``: una cadena de discos sobre ``x = L/2`` separa las
  mitades, como el disco central de la configuración actual.

El parámetro barrido es el semieje menor ``b``: con los focos fijos, es el
único grado de libertad geométrico de la idea.

Familia ``separacion``: cada elipse se traslada una distancia ``delta`` hacia
su arco. El foco externo queda detrás de la pared, a la altura del arco, y los
focos internos dejan de coincidir en el centro de la mesa. Se barren ``delta``
y ``b``.

Familia ``superelipse``: cada arco queda dentro de una sala
``|x'/A|^p + |y'/B|^p <= 1`` centrada a la altura del arco y corrida
``retroceso`` detrás de la pared. Generaliza a la elipse separada (``p = 2``)
y permite salas más puntiagudas (``p < 2``) o más rectangulares (``p > 2``).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import subprocess
import sys
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "cpp/build/release/tp3"
RAW = ROOT / "experiments/raw/elipses"
CONFIGS = RAW / "configs"
RESULTS = ROOT / "experiments/results/elipses"

sys.path.insert(0, str(ROOT / "python/src"))
sys.path.insert(0, str(ROOT / "scripts"))

from tp3analysis.goals import time_to_fraction  # noqa: E402
from tp3analysis.trajectory import read_trajectory  # noqa: E402

L, W, D, R = 1.20, 0.68, 0.20, 0.0175  # mesa, arco y radio de partícula
N = 100
GAP = 1e-4          # holgura entre discos consecutivos del contorno
GRID = 1e-3         # resolución de la grilla de accesibilidad
MARGIN = 1e-5       # holgura de los discos de relleno
ACCESS = 2e-5       # tolerancia para declarar accesible un punto de la grilla
BASE = [(0.60, 0.34, 0.34)]


@dataclass(frozen=True)
class Elipse:
    cx: float
    cy: float
    a: float
    b: float

    def punto(self, t: float) -> tuple[float, float]:
        return self.cx + self.a * math.cos(t), self.cy + self.b * math.sin(t)

    def normal(self, t: float) -> tuple[float, float]:
        nx, ny = self.b * math.cos(t), self.a * math.sin(t)
        norma = math.hypot(nx, ny)
        return nx / norma, ny / norma

    def distancia(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Distancia al interior (cero adentro), por bisección del multiplicador."""
        u = np.abs(np.asarray(x, dtype=float) - self.cx)
        v = np.abs(np.asarray(y, dtype=float) - self.cy)
        a2, b2 = self.a**2, self.b**2
        afuera = (u / self.a) ** 2 + (v / self.b) ** 2 > 1.0
        lo = np.zeros_like(u)
        hi = np.sqrt(a2 * u**2 + b2 * v**2)
        for _ in range(64):
            s = 0.5 * (lo + hi)
            g = (self.a * u / (s + a2)) ** 2 + (self.b * v / (s + b2)) ** 2 - 1.0
            lo = np.where(g > 0, s, lo)
            hi = np.where(g > 0, hi, s)
        s = 0.5 * (lo + hi)
        px, py = a2 * u / (s + a2), b2 * v / (s + b2)
        return np.where(afuera, np.hypot(u - px, v - py), 0.0)


@dataclass(frozen=True)
class Superelipse:
    cx: float
    cy: float
    a: float
    b: float
    p: float
    lado: str  # "izquierda" o "derecha": la mitad de la mesa que ocupa

    def punto(self, t: float) -> tuple[float, float]:
        c, s = math.cos(t), math.sin(t)
        e = 2 / self.p
        return (self.cx + self.a * math.copysign(abs(c) ** e, c),
                self.cy + self.b * math.copysign(abs(s) ** e, s))

    def normal(self, t: float) -> tuple[float, float]:
        c, s = math.cos(t), math.sin(t)
        e = 2 * (self.p - 1) / self.p
        nx = math.copysign(abs(c) ** e, c) / self.a
        ny = math.copysign(abs(s) ** e, s) / self.b
        norma = math.hypot(nx, ny)
        return nx / norma, ny / norma

    def _borde(self, muestras: int = 1500) -> tuple[np.ndarray, np.ndarray]:
        """Borde remuestreado a paso de arco uniforme."""
        t = np.linspace(0.0, 2 * math.pi, 40000)
        c, s = np.cos(t), np.sin(t)
        e = 2 / self.p
        x = self.cx + self.a * np.sign(c) * np.abs(c) ** e
        y = self.cy + self.b * np.sign(s) * np.abs(s) ** e
        arco = np.concatenate(([0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))))
        objetivo = np.linspace(0.0, arco[-1], muestras, endpoint=False)
        return np.interp(objetivo, arco, x), np.interp(objetivo, arco, y)

    def distancia(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Distancia al interior (cero adentro) por fuerza bruta contra el borde.

        Solo se calcula en la mitad de la mesa de la sala; en la otra devuelve
        infinito, lo que es exacto para la unión porque las salas son simétricas
        y cada una está contenida en su mitad.
        """
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        adentro = np.abs((x - self.cx) / self.a) ** self.p + np.abs((y - self.cy) / self.b) ** self.p <= 1
        propia = (x <= L / 2) if self.lado == "izquierda" else (x >= L / 2)
        resultado = np.full(x.shape, np.inf)
        resultado[adentro] = 0.0
        pendientes = np.flatnonzero((propia & ~adentro).ravel())
        bx, by = self._borde()
        planos_x, planos_y = x.ravel(), y.ravel()
        plano = resultado.ravel()
        for inicio in range(0, pendientes.size, 2048):
            idx = pendientes[inicio:inicio + 2048]
            d2 = (planos_x[idx, None] - bx[None, :]) ** 2 + (planos_y[idx, None] - by[None, :]) ** 2
            plano[idx] = np.sqrt(d2.min(axis=1))
        return plano.reshape(x.shape)


@dataclass(frozen=True)
class DisenoSuper:
    profundidad: float  # desde la línea de contacto con el arco hasta el fondo
    semiancho: float
    exponente: float
    retroceso: float    # cuánto se corre el centro detrás de la pared
    rho: float = R
    cuello: str = "superelipse"
    se_tocan: bool = False

    @property
    def etiqueta(self) -> str:
        return (f"super_P{self.profundidad * 1000:03.0f}_B{self.semiancho * 1000:03.0f}"
                f"_p{self.exponente * 100:03.0f}_s{self.retroceso * 1000:03.0f}"
                f"_rho{self.rho * 10000:03.0f}")

    def formas(self) -> tuple[Superelipse, Superelipse]:
        a = self.profundidad + self.retroceso
        cx = R - self.retroceso
        return (Superelipse(cx, W / 2, a, self.semiancho, self.exponente, "izquierda"),
                Superelipse(L - cx, W / 2, a, self.semiancho, self.exponente, "derecha"))

    def parametros(self) -> dict[str, object]:
        return {"cuello": self.cuello, "profundidad_m": self.profundidad,
                "semiancho_m": self.semiancho, "exponente": self.exponente,
                "retroceso_m": self.retroceso, "rho_m": self.rho}


@dataclass(frozen=True)
class Diseno:
    cuello: str
    b: float
    rho: float
    delta: float = 0.0

    @property
    def etiqueta(self) -> str:
        base = f"{self.cuello}_b{self.b * 1000:03.0f}_rho{self.rho * 10000:03.0f}"
        return base if self.delta == 0 else f"{base}_d{self.delta * 1000:03.0f}"

    @property
    def se_tocan(self) -> bool:
        """Las dos elipses se superponen en el centro de la mesa."""
        izquierda = self.elipses()[0]
        return izquierda.cx + izquierda.a > L / 2

    def elipses(self) -> tuple[Elipse, Elipse]:
        # Focos para los centros: (r, W/2) —el centro de una partícula que toca
        # el centro del arco— y (L/2, W/2), ambos corridos delta hacia el arco.
        c = (L / 2 - R) / 2
        cx = (L / 2 + R) / 2 - self.delta
        a = math.hypot(self.b, c)
        return Elipse(cx, W / 2, a, self.b), Elipse(L - cx, W / 2, a, self.b)

    def formas(self) -> tuple[Elipse, Elipse]:
        return self.elipses()

    def parametros(self) -> dict[str, object]:
        return {"cuello": self.cuello, "b_m": self.b, "a_m": self.elipses()[0].a,
                "rho_m": self.rho}


def _distancia_rectangulo(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    dx = np.maximum.reduce([R - x, x - (L - R), np.zeros_like(x)])
    dy = np.maximum.reduce([R - y, y - (W - R), np.zeros_like(y)])
    return np.hypot(dx, dy)


def distancia_arena(diseno: Diseno, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Cota inferior de la distancia a la región pensada para los centros."""
    izquierda, derecha = diseno.formas()
    rect = _distancia_rectangulo(x, y)
    di, dd = izquierda.distancia(x, y), derecha.distancia(x, y)
    if diseno.cuello == "cerrado":
        borde = L / 2 - diseno.rho - R
        di = np.maximum(di, np.maximum(x - borde, 0.0))
        dd = np.maximum(dd, np.maximum((L - borde) - x, 0.0))
    return np.maximum(np.minimum(di, dd), rect)


def _solapa(discos: list[tuple[float, float, float]], x: float, y: float, rho: float) -> bool:
    return any((x - a) ** 2 + (y - b) ** 2 < (rho + c) ** 2 for a, b, c in discos)


def _dentro(x: float, y: float, rho: float) -> bool:
    return rho <= x <= L - rho and rho <= y <= W - rho


def contorno(diseno: Diseno) -> list[tuple[float, float, float]]:
    rho, offset = diseno.rho, diseno.rho + R
    paso = 2 * rho + GAP
    discos: list[tuple[float, float, float]] = []

    if diseno.cuello == "cerrado" and diseno.se_tocan:
        izquierda = diseno.elipses()[0]
        borde = L / 2 - rho - R
        mitad = izquierda.b * math.sqrt(max(0.0, 1 - ((borde - izquierda.cx) / izquierda.a) ** 2))
        k = 0
        while k * paso <= mitad + offset:
            for signo in ((1,) if k == 0 else (1, -1)):
                y = W / 2 + signo * k * paso
                if _dentro(L / 2, y, rho):
                    discos.append((L / 2, y, rho))
            k += 1

    for indice, elipse in enumerate(diseno.formas()):
        otra = diseno.formas()[1 - indice]

        def q(t: float) -> tuple[float, float]:
            (px, py), (nx, ny) = elipse.punto(t), elipse.normal(t)
            return px + offset * nx, py + offset * ny

        t = 0.0
        while t < 2 * math.pi:
            x, y = q(t)
            conserva = _dentro(x, y, rho) and not _solapa(discos, x, y, rho)
            if conserva and diseno.cuello == "abierto":
                conserva = float(otra.distancia(np.array(x), np.array(y))) >= offset
            if conserva and diseno.cuello == "cerrado":
                conserva = (x < L / 2) if indice == 0 else (x > L / 2)
            if conserva:
                discos.append((x, y, rho))
            lo, hi = t, t + math.pi / 4
            for _ in range(60):
                medio = 0.5 * (lo + hi)
                xm, ym = q(medio)
                lo, hi = (medio, hi) if math.hypot(xm - x, ym - y) < paso else (lo, medio)
            t = hi
    return discos


class Grilla:
    def __init__(self) -> None:
        xs = np.arange(0.0, L + GRID / 2, GRID)
        ys = np.arange(0.0, W + GRID / 2, GRID)
        self.x, self.y = np.meshgrid(xs, ys, indexing="ij")
        self.holgura = np.minimum.reduce([self.x, L - self.x, self.y, W - self.y])

    def agregar(self, x: float, y: float, rho: float) -> None:
        np.minimum(self.holgura, np.hypot(self.x - x, self.y - y) - rho, out=self.holgura)

    def accesible(self) -> np.ndarray:
        return self.holgura >= R + ACCESS

    def conectado_a_arcos(self) -> np.ndarray:
        libre = self.holgura >= R
        visto = np.zeros_like(libre)
        cola = deque()
        semillas = libre & (self.x <= R + GRID) & (np.abs(self.y - W / 2) <= D / 2)
        semillas |= libre & (self.x >= L - R - GRID) & (np.abs(self.y - W / 2) <= D / 2)
        for i, j in zip(*np.nonzero(semillas)):
            visto[i, j] = True
            cola.append((i, j))
        nx, ny = libre.shape
        while cola:
            i, j = cola.popleft()
            for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= a < nx and 0 <= b < ny and libre[a, b] and not visto[a, b]:
                    visto[a, b] = True
                    cola.append((a, b))
        return visto


def construir(diseno: Diseno) -> dict[str, object] | None:
    """Genera el archivo de obstáculos y sus diagnósticos geométricos.

    Devuelve ``None`` si la elipse no deja ningún disco dentro de la mesa: con
    ``b`` grande cubre todo el dominio y el diseño degenera en la mesa vacía.
    """
    discos = contorno(diseno)
    grilla = Grilla()
    for disco in discos:
        grilla.agregar(*disco)
    lejos = distancia_arena(diseno, grilla.x, grilla.y)
    rellenable = lejos >= diseno.rho + R
    tope = lejos - R
    rellenos = 0
    while True:
        candidatos = rellenable & grilla.accesible()
        if not candidatos.any():
            break
        radio = np.where(candidatos, np.minimum(grilla.holgura, tope), -1.0)
        k = np.unravel_index(np.argmax(radio), radio.shape)
        disco = (float(grilla.x[k]), float(grilla.y[k]), float(radio[k]) - MARGIN)
        discos.append(disco)
        grilla.agregar(*disco)
        rellenos += 1

    if not discos:
        return None
    discos = [(round(x, 6), round(y, 6), math.floor(rho * 1e6) / 1e6) for x, y, rho in discos]
    validar(discos)
    libre = grilla.holgura >= R
    conectado = grilla.conectado_a_arcos()
    celda = GRID**2
    CONFIGS.mkdir(parents=True, exist_ok=True)
    ruta = CONFIGS / f"{diseno.etiqueta}.txt"
    ruta.write_text("".join(f"{x:.6f} {y:.6f} {rho:.6f}\n" for x, y, rho in discos))
    area = float(libre.sum() * celda)
    return {
        "label": diseno.etiqueta,
        **diseno.parametros(),
        "obstaculos": len(discos),
        "rellenos": rellenos,
        "area_centros_m2": area,
        "fraccion_atrapada": float((libre & ~conectado).sum() / libre.sum()),
        "ruta": str(ruta.relative_to(ROOT)),
    }


def validar(discos: list[tuple[float, float, float]]) -> None:
    arr = np.array(discos)
    if (arr[:, 2] < R).any():
        raise ValueError("hay un obstáculo con radio menor que r")
    if ((arr[:, 0] - arr[:, 2] < 0) | (arr[:, 0] + arr[:, 2] > L)
            | (arr[:, 1] - arr[:, 2] < 0) | (arr[:, 1] + arr[:, 2] > W)).any():
        raise ValueError("hay un obstáculo fuera del dominio")
    dx = arr[:, None, 0] - arr[None, :, 0]
    dy = arr[:, None, 1] - arr[None, :, 1]
    suma = arr[:, None, 2] + arr[None, :, 2]
    solape = dx**2 + dy**2 < suma**2
    np.fill_diagonal(solape, False)
    if solape.any():
        raise ValueError("hay obstáculos solapados")


def correr(trabajo: tuple[str, str, int, float]) -> dict[str, object]:
    etiqueta, ruta, semilla, tmax = trabajo
    salida = RAW / "tray" / f"{etiqueta}_s{semilla}.txt"
    salida.parent.mkdir(parents=True, exist_ok=True)
    comando = [str(ENGINE), "simulate", "--n", str(N), "--seed", str(semilla),
               "--tmax", str(tmax), "--save-every", "0", "--output", str(salida)]
    if ruta:
        comando += ["--config", str(ROOT / ruta)]
    proceso = subprocess.run(comando, capture_output=True, text=True)
    if proceso.returncode != 0:
        # Típicamente: la arena no alcanza para generar las N partículas.
        salida.unlink(missing_ok=True)
        return {"label": etiqueta, "seed": semilla, "tmax_s": tmax, "reached": 0,
                "t90_seconds": "", "goals_at_end": 0,
                "error": proceso.stderr.strip().splitlines()[-1]}
    resultado = time_to_fraction(read_trajectory(salida))
    salida.unlink()
    return {
        "label": etiqueta, "seed": semilla, "tmax_s": tmax,
        "reached": int(resultado.reached),
        "t90_seconds": "" if resultado.t90 is None else resultado.t90,
        "goals_at_end": resultado.goals_at_end,
        "error": "",
    }


def evaluar(configs: list[dict[str, object]], semillas: range, tmax: float,
            etapa: str) -> list[dict[str, object]]:
    trabajos = [(c["label"], c["ruta"], s, tmax) for c in configs for s in semillas]
    with ProcessPoolExecutor() as pool:
        filas = list(pool.map(correr, trabajos, chunksize=4))
    for fila in filas:
        fila["etapa"] = etapa
    return filas


def resumir(configs: list[dict[str, object]], filas: list[dict[str, object]]) -> list[dict[str, object]]:
    resumen = []
    for config in configs:
        propias = [f for f in filas if f["label"] == config["label"]]
        t90 = [float(f["t90_seconds"]) for f in propias if f["reached"]]
        media = statistics.fmean(t90) if t90 else math.nan
        desvio = statistics.stdev(t90) if len(t90) > 1 else math.nan
        resumen.append({
            **{k: v for k, v in config.items() if k != "ruta"},
            "realizaciones": len(propias),
            "alcanzaron": len(t90),
            "mean_t90_seconds": media,
            "std_t90_seconds": desvio,
            "sem_t90_seconds": desvio / math.sqrt(len(t90)) if len(t90) > 1 else math.nan,
            "mean_goals_at_end": statistics.fmean(f["goals_at_end"] for f in propias),
            "errores": sum(1 for f in propias if f["error"]),
        })
    return resumen


def escribir(ruta: Path, filas: list[dict[str, object]]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    campos = list(dict.fromkeys(k for fila in filas for k in fila))
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos, restval="", lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)


def referencias() -> list[dict[str, object]]:
    CONFIGS.mkdir(parents=True, exist_ok=True)
    ruta = CONFIGS / "actual.txt"
    ruta.write_text("".join(f"{x:.2f} {y:.2f} {rho:.2f}\n" for x, y, rho in BASE))
    return [
        {"label": "vacia", "cuello": "", "b_m": "", "a_m": "", "rho_m": "", "obstaculos": 0,
         "rellenos": 0, "area_centros_m2": "", "fraccion_atrapada": 0.0, "ruta": ""},
        {"label": "actual", "cuello": "", "b_m": "", "a_m": "", "rho_m": "", "obstaculos": 1,
         "rellenos": 0, "area_centros_m2": "", "fraccion_atrapada": 0.0,
         "ruta": str(ruta.relative_to(ROOT))},
    ]


def construir_todos(disenos: list[Diseno]) -> list[dict[str, object]]:
    with ProcessPoolExecutor() as pool:
        return [c for c in pool.map(construir, disenos) if c is not None]


def validos(resumen: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        (f for f in resumen if f["cuello"] and f["alcanzaron"] == f["realizaciones"]
         and f["fraccion_atrapada"] == 0.0),
        key=lambda f: f["mean_t90_seconds"],
    )


def etapa_barrido() -> None:
    disenos = [Diseno(cuello, round(b, 3), R)
               for cuello in ("abierto", "cerrado")
               for b in np.arange(0.100, 0.5001, 0.025)]
    configs = construir_todos(disenos)
    escribir(RESULTS / "plan_barrido.csv", configs)
    configs += referencias()
    filas = evaluar(configs, range(5000, 5016), 60.0, "barrido")
    escribir(RESULTS / "t90_runs_barrido.csv", filas)
    escribir(RESULTS / "t90_summary_barrido.csv", resumir(configs, filas))


def _leer(ruta: Path) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def _numerico(filas: list[dict[str, str]]) -> list[dict[str, object]]:
    salida = []
    for fila in filas:
        convertida: dict[str, object] = {}
        for k, v in fila.items():
            try:
                convertida[k] = float(v) if k not in ("label", "cuello", "ruta") else v
            except ValueError:
                convertida[k] = v
        salida.append(convertida)
    return salida


def etapa_refinamiento() -> None:
    resumen = validos(_numerico(_leer(RESULTS / "t90_summary_barrido.csv")))
    disenos: list[Diseno] = []
    for cuello in ("abierto", "cerrado"):
        mejor = next(f for f in resumen if f["cuello"] == cuello)
        centro = float(mejor["b_m"])
        disenos += [Diseno(cuello, round(b, 3), R)
                    for b in np.arange(centro - 0.025, centro + 0.02501, 0.005) if b >= 0.05]
    configs = construir_todos(disenos)
    escribir(RESULTS / "plan_refinamiento.csv", configs)
    filas = evaluar(configs, range(6000, 6024), 60.0, "refinamiento")
    escribir(RESULTS / "t90_runs_refinamiento.csv", filas)
    escribir(RESULTS / "t90_summary_refinamiento.csv", resumir(configs, filas))


def etapa_final() -> None:
    """Semillas nuevas y tmax de la competencia para no elegir con ruido."""
    resumen = validos(_numerico(_leer(RESULTS / "t90_summary_refinamiento.csv")))
    finalistas = [Diseno(f["cuello"], float(f["b_m"]), R) for f in resumen[:3]]
    mejor = finalistas[0]
    # Control de precisión del espejo: misma arena para los centros, discos más
    # grandes y por lo tanto festones más profundos.
    controles = [Diseno(mejor.cuello, mejor.b, rho) for rho in (2 * R, 3 * R)]
    configs = construir_todos(finalistas + controles) + referencias()
    escribir(RESULTS / "plan_final.csv", configs)
    filas = evaluar(configs, range(7000, 7040), 100.0, "final")
    escribir(RESULTS / "t90_runs_final.csv", filas)
    escribir(RESULTS / "t90_summary_final.csv", resumir(configs, filas))


def _disenos_separacion(deltas, bs) -> list[Diseno]:
    disenos = []
    for delta in deltas:
        for b in bs:
            for cuello in ("abierto", "cerrado"):
                diseno = Diseno(cuello, round(float(b), 3), R, round(float(delta), 3))
                # Si no se tocan, las dos variantes son la misma configuración.
                if cuello == "cerrado" and not diseno.se_tocan:
                    continue
                disenos.append(diseno)
    return disenos


def etapa_separacion_barrido() -> None:
    disenos = _disenos_separacion(np.arange(0.0, 0.301, 0.05), np.arange(0.15, 0.4501, 0.05))
    configs = construir_todos(disenos)
    escribir(RESULTS / "plan_separacion_barrido.csv", configs)
    configs += referencias()
    filas = evaluar(configs, range(5000, 5016), 60.0, "separacion_barrido")
    escribir(RESULTS / "t90_runs_separacion_barrido.csv", filas)
    escribir(RESULTS / "t90_summary_separacion_barrido.csv", resumir(configs, filas))


def etapa_separacion_refinamiento() -> None:
    resumen = validos(_numerico(_leer(RESULTS / "t90_summary_separacion_barrido.csv")))
    plan = {f["label"]: f for f in _numerico(_leer(RESULTS / "plan_separacion_barrido.csv"))}
    mejor = resumen[0]
    delta = _delta(plan[mejor["label"]]["label"])
    b = float(mejor["b_m"])
    disenos = [d for d in _disenos_separacion(
        np.arange(max(0.0, delta - 0.03), delta + 0.0301, 0.015),
        np.arange(b - 0.03, b + 0.0301, 0.015),
    ) if d.cuello == mejor["cuello"] or not d.se_tocan]
    configs = construir_todos(disenos)
    escribir(RESULTS / "plan_separacion_refinamiento.csv", configs)
    filas = evaluar(configs, range(6000, 6024), 60.0, "separacion_refinamiento")
    escribir(RESULTS / "t90_runs_separacion_refinamiento.csv", filas)
    escribir(RESULTS / "t90_summary_separacion_refinamiento.csv", resumir(configs, filas))


def etapa_separacion_final() -> None:
    resumen = validos(_numerico(_leer(RESULTS / "t90_summary_separacion_refinamiento.csv")))
    finalistas = [Diseno(f["cuello"], float(f["b_m"]), R, _delta(f["label"])) for f in resumen[:3]]
    configs = construir_todos(finalistas) + referencias()
    escribir(RESULTS / "plan_separacion_final.csv", configs)
    filas = evaluar(configs, range(8000, 8040), 100.0, "separacion_final")
    escribir(RESULTS / "t90_runs_separacion_final.csv", filas)
    escribir(RESULTS / "t90_summary_separacion_final.csv", resumir(configs, filas))


def etapa_separacion_extension() -> None:
    """El óptimo del refinamiento quedó en el borde (delta máximo): se extiende."""
    disenos = [d for d in _disenos_separacion(np.arange(0.33, 0.4501, 0.02),
                                              np.arange(0.22, 0.3401, 0.02))
               if d.cuello == "abierto"]
    configs = construir_todos(disenos)
    escribir(RESULTS / "plan_separacion_extension.csv", configs)
    filas = evaluar(configs, range(6000, 6024), 60.0, "separacion_extension")
    escribir(RESULTS / "t90_runs_separacion_extension.csv", filas)
    escribir(RESULTS / "t90_summary_separacion_extension.csv", resumir(configs, filas))


def etapa_separacion_final_extendida() -> None:
    """Finalistas de refinamiento + extensión (mismas semillas), con semillas nuevas."""
    resumen = validos(
        _numerico(_leer(RESULTS / "t90_summary_separacion_refinamiento.csv"))
        + _numerico(_leer(RESULTS / "t90_summary_separacion_extension.csv"))
    )
    finalistas = [Diseno(f["cuello"], float(f["b_m"]), R, _delta(f["label"])) for f in resumen[:4]]
    previo = Diseno("abierto", 0.265, R, 0.33)
    if previo not in finalistas:
        finalistas.append(previo)
    configs = construir_todos(finalistas) + referencias()
    escribir(RESULTS / "plan_separacion_final_extendida.csv", configs)
    filas = evaluar(configs, range(9000, 9040), 100.0, "separacion_final_extendida")
    escribir(RESULTS / "t90_runs_separacion_final_extendida.csv", filas)
    escribir(RESULTS / "t90_summary_separacion_final_extendida.csv", resumir(configs, filas))


MEJOR_ELIPSE = Diseno("abierto", 0.30, R, 0.39)


def diseno_desde(fila: dict[str, object]) -> Diseno | DisenoSuper:
    if fila["cuello"] == "superelipse":
        return DisenoSuper(float(fila["profundidad_m"]), float(fila["semiancho_m"]),
                           float(fila["exponente"]), float(fila["retroceso_m"]))
    return Diseno(str(fila["cuello"]), float(fila["b_m"]), R, _delta(str(fila["label"])))


def _hipercubo(muestras: int, rangos: list[tuple[float, float]], semilla: int) -> np.ndarray:
    """Hipercubo latino: cada parámetro cubre sus estratos una vez."""
    rng = np.random.default_rng(semilla)
    puntos = np.empty((muestras, len(rangos)))
    for j, (lo, hi) in enumerate(rangos):
        estratos = (rng.permutation(muestras) + rng.random(muestras)) / muestras
        puntos[:, j] = lo + estratos * (hi - lo)
    return puntos


def etapa_super_barrido() -> None:
    puntos = _hipercubo(80, [(0.22, 0.45), (0.20, 0.40), (1.3, 5.0), (0.0, 0.20)], 20260925)
    disenos = [DisenoSuper(round(P, 3), round(B, 3), round(e, 2), round(s, 3))
               for P, B, e, s in puntos]
    configs = construir_todos(disenos + [MEJOR_ELIPSE])
    escribir(RESULTS / "plan_super_barrido.csv", configs)
    configs += referencias()[1:]
    filas = evaluar(configs, range(5000, 5016), 60.0, "super_barrido")
    escribir(RESULTS / "t90_runs_super_barrido.csv", filas)
    escribir(RESULTS / "t90_summary_super_barrido.csv", resumir(configs, filas))


def _vecinos(d: DisenoSuper) -> list[DisenoSuper]:
    pasos = {"profundidad": 0.02, "semiancho": 0.02, "exponente": 0.4, "retroceso": 0.03}
    minimos = {"profundidad": 0.15, "semiancho": 0.15, "exponente": 1.2, "retroceso": 0.0}
    salida = []
    for campo, paso in pasos.items():
        for signo in (-1, 1):
            valor = round(getattr(d, campo) + signo * paso, 3)
            if valor >= minimos[campo]:
                salida.append(DisenoSuper(**{**{k: getattr(d, k) for k in pasos}, campo: valor}))
    return salida


def etapa_super_refinamiento() -> None:
    resumen = validos(_numerico(_leer(RESULTS / "t90_summary_super_barrido.csv")))
    mejores = [diseno_desde(f) for f in resumen if f["cuello"] == "superelipse"][:8]
    disenos = list(mejores)
    for centro in mejores[:3]:
        disenos += [v for v in _vecinos(centro) if v not in disenos]
    configs = construir_todos(disenos + [MEJOR_ELIPSE])
    escribir(RESULTS / "plan_super_refinamiento.csv", configs)
    filas = evaluar(configs, range(6000, 6024), 60.0, "super_refinamiento")
    escribir(RESULTS / "t90_runs_super_refinamiento.csv", filas)
    escribir(RESULTS / "t90_summary_super_refinamiento.csv", resumir(configs, filas))


def etapa_super_final() -> None:
    resumen = validos(_numerico(_leer(RESULTS / "t90_summary_super_refinamiento.csv")))
    finalistas = [diseno_desde(f) for f in resumen[:4]]
    if MEJOR_ELIPSE not in finalistas:
        finalistas.append(MEJOR_ELIPSE)
    configs = construir_todos(finalistas) + referencias()[1:]
    escribir(RESULTS / "plan_super_final.csv", configs)
    filas = evaluar(configs, range(10000, 10040), 100.0, "super_final")
    escribir(RESULTS / "t90_runs_super_final.csv", filas)
    escribir(RESULTS / "t90_summary_super_final.csv", resumir(configs, filas))


# Configuración adoptada tras el desempate con 100 semillas nuevas.
ELEGIDA = DisenoSuper(0.277, 0.268, 4.72, 0.113)
FINAL_CONFIG = ROOT / "experiments/configs/SdS_TP3_2026Q2G07CS_Config.txt"
FIGURAS = ROOT / "experiments/figures/elipses"
VIDEOS = ROOT / "videos"
# Prioridad de las mediciones de t90: más semillas y sin sesgo de selección primero.
FUENTES_T90 = ("desempate", "super_final", "separacion_final_extendida", "separacion_final",
               "final", "super_refinamiento", "separacion_extension",
               "separacion_refinamiento", "refinamiento", "super_barrido",
               "separacion_barrido", "barrido")


def etapa_adoptar() -> None:
    """Escribe el archivo de la competencia y verifica la restricción ii."""
    config = construir(ELEGIDA)
    assert config is not None and config["fraccion_atrapada"] == 0.0
    FINAL_CONFIG.write_bytes((ROOT / str(config["ruta"])).read_bytes())
    fallas = []
    for semilla in range(20000, 21000):
        proceso = subprocess.run(
            [str(ENGINE), "generate", "--n", str(N), "--seed", str(semilla),
             "--config", str(FINAL_CONFIG), "--output", "/dev/null"],
            capture_output=True, text=True,
        )
        if proceso.returncode != 0:
            fallas.append(semilla)
    if fallas:
        raise RuntimeError(f"la generación falló para las semillas {fallas[:10]}")
    desempate = {f["label"]: f for f in _numerico(_leer(RESULTS / "t90_summary_desempate.csv"))}
    elegida = desempate[ELEGIDA.etiqueta]
    seleccion = {
        "label": ELEGIDA.etiqueta,
        **ELEGIDA.parametros(),
        "obstaculos": config["obstaculos"],
        "area_centros_m2": config["area_centros_m2"],
        "config": str(FINAL_CONFIG.relative_to(ROOT)),
        "generaciones_verificadas": 1000,
        "t90_desempate": {
            "semillas": [11000, 11099],
            "tmax_s": 100.0,
            "mean_s": elegida["mean_t90_seconds"],
            "std_s": elegida["std_t90_seconds"],
            "sem_s": elegida["sem_t90_seconds"],
        },
        "t90_referencias_desempate": {
            label: {"mean_s": f["mean_t90_seconds"], "sem_s": f["sem_t90_seconds"]}
            for label, f in desempate.items() if label != ELEGIDA.etiqueta
        },
    }
    (RESULTS / "seleccion.json").write_text(
        json.dumps(seleccion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"adoptada {ELEGIDA.etiqueta}: {config['obstaculos']} obstáculos, "
          f"1000 generaciones sin fallas")


def _t90_por_etiqueta() -> dict[str, tuple[float, float, int, str]]:
    salida: dict[str, tuple[float, float, int, str]] = {}
    for fuente in FUENTES_T90:
        ruta = RESULTS / f"t90_summary_{fuente}.csv"
        if not ruta.exists():
            continue
        for fila in _numerico(_leer(ruta)):
            if fila["label"] not in salida and fila["alcanzaron"] == fila["realizaciones"]:
                salida[str(fila["label"])] = (float(fila["mean_t90_seconds"]),
                                              float(fila["sem_t90_seconds"]),
                                              int(fila["realizaciones"]), fuente)
    return salida


def _difusion(trabajo: tuple[str, str, bool]) -> dict[str, object]:
    """Mismo protocolo que ``run_experiments.run_diffusion``."""
    import run_experiments as rx
    from tp3analysis.diffusion import summarize_diffusion
    from tp3analysis.msd import trajectory_msd

    etiqueta, ruta, guardar_curvas = trabajo
    curvas = []
    for repeticion in range(rx.DIFFUSION_REPETITIONS):
        semilla = 3000 + repeticion
        salida = RAW / "difusion" / f"{etiqueta}_s{semilla}.txt"
        salida.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [str(ENGINE), "simulate", "--n", str(N), "--seed", str(semilla),
             "--tmax", str(rx.DIFFUSION_TMAX), "--save-every", str(rx.DIFFUSION_SAVE_EVERY),
             "--config", str(ROOT / ruta), "--output", str(salida)],
            check=True, capture_output=True, text=True,
        )
        curvas.append(trajectory_msd(read_trajectory(salida), rx.DIFFUSION_BIN_WIDTH,
                                     rx.DIFFUSION_MAX_LAG,
                                     single_origin=rx.DIFFUSION_SINGLE_ORIGIN))
        salida.unlink()
    resumen = summarize_diffusion(curvas, rx.DIFFUSION_WINDOW)
    if guardar_curvas:
        curva = resumen.pooled_curve
        escribir(RESULTS / f"msd_{etiqueta}.csv", [
            {"lag_seconds": a, "msd_m2": b, "std_m2": c}
            for a, b, c in zip(curva.lags, curva.msd, curva.std)])
        escribir(RESULTS / f"ec_{etiqueta}.csv", [
            {"slope_m2_s": a, "squared_error": b}
            for a, b in zip(resumen.pooled.fit.sweep_c, resumen.pooled.fit.sweep_error)])
    return {
        "label": etiqueta,
        "mean_D_m2_s": resumen.plain.mean,
        "std_D_m2_s": resumen.plain.std,
        "sem_D_m2_s": resumen.plain.sem,
        "pooled_D_m2_s": resumen.pooled.coefficient,
        "pooled_fit_error_m2_s": resumen.pooled.error,
    }


def etapa_difusion() -> None:
    """D para todas las configuraciones de las búsquedas nuevas (punto 1.3)."""
    familias = {"barrido": "elipse_focos_fijos", "separacion_barrido": "elipse_separada",
                "super_barrido": "superelipse"}
    configs: dict[str, tuple[str, str]] = {}
    for plan, familia in familias.items():
        for fila in _leer(RESULTS / f"plan_{plan}.csv"):
            configs.setdefault(fila["label"], (familia, fila["ruta"]))
    for diseno, familia in ((MEJOR_ELIPSE, "elipse_separada"), (ELEGIDA, "superelipse")):
        config = construir(diseno)
        configs[diseno.etiqueta] = (familia, str(config["ruta"]))
    t90 = _t90_por_etiqueta()
    trabajos = [(etiqueta, ruta, etiqueta in (ELEGIDA.etiqueta, MEJOR_ELIPSE.etiqueta))
                for etiqueta, (_, ruta) in configs.items() if etiqueta in t90]
    with ProcessPoolExecutor() as pool:
        filas = list(pool.map(_difusion, trabajos))
    # Las configuraciones de un solo disco ya tienen D con el mismo protocolo.
    previas = {f["label"]: f for f in _leer(ROOT / "experiments/results/diffusion_summary.csv")}
    t90_previas = {f["label"]: f for f in _leer(ROOT / "experiments/results/t90_summary.csv")}
    for etiqueta, fila in previas.items():
        filas.append({k: float(v) for k, v in fila.items() if k.endswith("m2_s")} | {"label": etiqueta})
        previa = t90_previas[etiqueta]
        t90[etiqueta] = (float(previa["mean_t90_seconds"]), float(previa["sem_t90_seconds"]),
                         int(previa["realizations"]), "run_experiments")
        configs[etiqueta] = ("vacia" if etiqueta == "vacia" else "disco_unico", "")
    for fila in filas:
        media, error, n, fuente = t90[fila["label"]]
        fila.update({"familia": configs[fila["label"]][0], "mean_t90_seconds": media,
                     "sem_t90_seconds": error, "realizaciones_t90": n, "fuente_t90": fuente})
    escribir(RESULTS / "difusion_todas.csv", filas)
    d = np.array([f["mean_D_m2_s"] for f in filas])
    t = np.array([f["mean_t90_seconds"] for f in filas])
    print(f"{len(filas)} configuraciones; Pearson r(D, t90) = {np.corrcoef(d, t)[0, 1]:.3f}")
    for familia in sorted({f["familia"] for f in filas}):
        sel = [f for f in filas if f["familia"] == familia]
        if len(sel) > 2:
            r = np.corrcoef([f["mean_D_m2_s"] for f in sel], [f["mean_t90_seconds"] for f in sel])[0, 1]
            print(f"  {familia:20s} n={len(sel):3d} r={r:+.3f}")


def etapa_unir_difusion() -> None:
    """Refresca las columnas de t90 de difusion_todas.csv sin recalcular D."""
    filas = _numerico(_leer(RESULTS / "difusion_todas.csv"))
    t90 = _t90_por_etiqueta()
    previas = {f["label"]: f for f in _leer(ROOT / "experiments/results/t90_summary.csv")}
    for etiqueta, previa in previas.items():
        t90[etiqueta] = (float(previa["mean_t90_seconds"]), float(previa["sem_t90_seconds"]),
                         int(previa["realizations"]), "run_experiments")
    for fila in filas:
        media, error, n, fuente = t90[str(fila["label"])]
        fila.update({"mean_t90_seconds": media, "sem_t90_seconds": error,
                     "realizaciones_t90": n, "fuente_t90": fuente})
    escribir(RESULTS / "difusion_todas.csv", filas)
    d = np.array([float(f["mean_D_m2_s"]) for f in filas])
    t = np.array([float(f["mean_t90_seconds"]) for f in filas])
    print(f"{len(filas)} configuraciones; Pearson r(D, t90) = {np.corrcoef(d, t)[0, 1]:.3f}")


def _simular_animacion(etiqueta: str, ruta: str, semilla: int, t90: float) -> None:
    from tp3analysis.animation import render_animation, render_snapshot

    salida = ROOT / "data/generated" / f"anim_{etiqueta}.txt"
    salida.parent.mkdir(parents=True, exist_ok=True)
    comando = [str(ENGINE), "simulate", "--n", str(N), "--seed", str(semilla), "--tmax", "30",
               "--save-every", "20", "--output", str(salida)]
    if ruta:
        comando += ["--config", str(ROOT / ruta)]
    subprocess.run(comando, check=True, capture_output=True, text=True)
    trayectoria = read_trajectory(salida)
    cuadros = np.flatnonzero(np.array(trayectoria.reasons) != "final")
    cuadro = int(cuadros[np.argmin(abs(trayectoria.times[cuadros] - 0.65 * t90))])
    render_snapshot(trayectoria, FIGURAS / f"anim-{etiqueta}.png", cuadro)
    render_animation(trayectoria, VIDEOS / f"anim-{etiqueta}.mp4", fps=30, duration=15)


def _semilla_representativa(corridas: str, etiqueta: str) -> tuple[int, float]:
    """La realización cuyo t90 queda más cerca de la media de su configuración."""
    filas = [f for f in _leer(RESULTS / corridas) if f["label"] == etiqueta and f["reached"] == "1"]
    media = statistics.fmean(float(f["t90_seconds"]) for f in filas)
    elegida = min(filas, key=lambda f: abs(float(f["t90_seconds"]) - media))
    return int(elegida["seed"]), float(elegida["t90_seconds"])


def etapa_animaciones() -> None:
    import os
    os.environ.setdefault("MPLBACKEND", "Agg")
    previa = json.loads((ROOT / "experiments/results/selection.json").read_text(encoding="utf-8"))
    semilla, t90 = _semilla_representativa("t90_runs_desempate.csv", ELEGIDA.etiqueta)
    trabajos = [
        ("vacia", "", previa["vacia"]["seed"], previa["vacia"]["t90_seconds"]),
        ("disco", "experiments/raw/elipses/configs/actual.txt",
         previa["mejor"]["seed"], previa["mejor"]["t90_seconds"]),
        ("elegida", str(FINAL_CONFIG.relative_to(ROOT)), semilla, t90),
    ]
    with ProcessPoolExecutor() as pool:
        list(pool.map(_simular_animacion, *zip(*trabajos)))
    seleccion = json.loads((RESULTS / "seleccion.json").read_text(encoding="utf-8"))
    seleccion["animaciones"] = {
        etiqueta: {"semilla": s, "t90_s": t, "trayectoria": f"data/generated/anim_{etiqueta}.txt",
                   "video": f"videos/anim-{etiqueta}.mp4",
                   "fotograma": f"experiments/figures/elipses/anim-{etiqueta}.png"}
        for etiqueta, _, s, t in trabajos
    }
    (RESULTS / "seleccion.json").write_text(
        json.dumps(seleccion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _delta(etiqueta: str) -> float:
    for parte in etiqueta.split("_"):
        if parte.startswith("d") and parte[1:].isdigit():
            return int(parte[1:]) / 1000
    return 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("etapa", choices=("barrido", "refinamiento", "final", "todo", "construir",
                                          "separacion", "separacion-refinamiento",
                                          "separacion-final", "separacion-todo",
                                          "separacion-extension", "super",
                                          "super-refinamiento", "super-final", "super-todo",
                                          "adoptar", "difusion", "animaciones",
                                          "unir-difusion"))
    parser.add_argument("--cuello", default="abierto")
    parser.add_argument("--b", type=float, default=0.25)
    parser.add_argument("--rho", type=float, default=R)
    parser.add_argument("--delta", type=float, default=0.0)
    args = parser.parse_args()
    if args.etapa == "construir":
        print(construir(Diseno(args.cuello, args.b, args.rho, args.delta)) or "diseño degenerado: mesa vacía")
        return 0
    etapas = {"barrido": [etapa_barrido], "refinamiento": [etapa_refinamiento],
              "final": [etapa_final],
              "todo": [etapa_barrido, etapa_refinamiento, etapa_final],
              "separacion": [etapa_separacion_barrido],
              "separacion-refinamiento": [etapa_separacion_refinamiento],
              "separacion-final": [etapa_separacion_final],
              "separacion-extension": [etapa_separacion_extension,
                                       etapa_separacion_final_extendida],
              "super": [etapa_super_barrido],
              "super-refinamiento": [etapa_super_refinamiento],
              "super-final": [etapa_super_final],
              "super-todo": [etapa_super_barrido, etapa_super_refinamiento, etapa_super_final],
              "adoptar": [etapa_adoptar],
              "difusion": [etapa_difusion],
              "unir-difusion": [etapa_unir_difusion],
              "animaciones": [etapa_animaciones],
              "separacion-todo": [etapa_separacion_barrido, etapa_separacion_refinamiento,
                                  etapa_separacion_final]}[args.etapa]
    for etapa in etapas:
        etapa()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
