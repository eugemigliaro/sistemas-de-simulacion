"""Genera las animaciones de la presentación a partir de una trayectoria del motor.

Uso:

    python -m tp3analysis.animar trayectoria.txt --video anim.mp4 [--fotograma anim.png]

Es un módulo independiente del motor: solo lee el archivo de texto que el
motor escribió [TP03, p. 1]. La animación va en tiempo real (1 s de video =
1 s simulado), con F_u(t) dibujándose debajo y t90 marcado.

**No se interpola entre eventos.** Cada cuadro del video muestra el último
estado que el motor calculó en un evento anterior o igual a ese instante
(``animation.event_frames_at``): las posiciones se dibujan tal cual están en la
trayectoria. El cuadro "final", que es un avance en línea recta hasta tmax y no
un evento, nunca se muestra.

Las animaciones de la presentación salieron de estas trayectorias:

    tp3 simulate --n 100 --seed 12018 --tmax 30 --save-every 10 --output vacia.txt
    tp3 simulate --n 100 --seed 11091 --tmax 30 --save-every 10 \\
        --config SdS_TP3_2026Q2G07CS_Config.txt --output elegida.txt
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")

from .animation import render_goal_animation, render_goal_snapshot  # noqa: E402
from .goals import time_to_fraction  # noqa: E402
from .trajectory import Trajectory, read_trajectory  # noqa: E402

MARGEN = 4.0  # segundos de video después de t90


def duracion(trayectoria: Trajectory) -> float:
    """Hasta unos segundos después de t90, sin pasar del tiempo simulado."""
    t90 = time_to_fraction(trayectoria).t90
    if t90 is None:
        return trayectoria.final_time
    return min(trayectoria.final_time, float(math.ceil(t90 + MARGEN)))


def animar(trayectoria: Path, video: Path, fotograma: Path | None = None,
           fps: int = 30) -> tuple[float, float | None]:
    """Escribe el MP4 y, si se pide, el fotograma para el PDF (t90 + 1 s)."""
    datos = read_trajectory(trayectoria)
    fin = duracion(datos)
    t90 = time_to_fraction(datos).t90
    if fotograma is not None:
        instante = min(t90 + 1.0, fin) if t90 is not None else fin / 2
        render_goal_snapshot(datos, fotograma, instante, fin)
    render_goal_animation(datos, video, fin, fps)
    return fin, t90


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tp3analysis.animar",
        description="Animación en tiempo real con F_u(t), sin interpolar entre eventos.",
    )
    parser.add_argument("trayectoria", type=Path, help="archivo escrito por tp3 simulate")
    parser.add_argument("--video", type=Path, required=True, help="MP4 de salida")
    parser.add_argument("--fotograma", type=Path, help="PNG del fotograma para el PDF")
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args(argv)
    fin, t90 = animar(args.trayectoria, args.video, args.fotograma, args.fps)
    texto_t90 = "no se alcanzó" if t90 is None else f"{t90:.2f} s"
    print(f"{args.video}: {fin:.0f} s de video; t90 = {texto_t90}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
