"""Interfaz de línea de comandos del postproceso."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from tp1viz import __version__
from tp1viz.metrics import (
    MetricsError,
    read_metrics,
    summarize_metrics,
    write_summaries,
)
from tp1viz.particles import ParticleDataError, read_neighbors, read_system


def _run_plot_m(arguments: argparse.Namespace) -> int:
    from tp1viz.plot_m import plot_m

    metrics = read_metrics(arguments.inputs)
    summaries = summarize_metrics(metrics)
    write_summaries(arguments.summary, summaries)
    plot_m(
        summaries,
        arguments.figure,
        log_x=arguments.log_x,
        log_y=arguments.log_y,
    )
    print(f"Resumen escrito en {arguments.summary}")
    print(f"Figura escrita en {arguments.figure}")
    return 0


def _run_plot_neighbors(arguments: argparse.Namespace) -> int:
    from tp1viz.plot_neighbors import plot_neighbors

    system = read_system(arguments.static, arguments.dynamic)
    neighbors = read_neighbors(arguments.neighbors, len(system.particles))
    plot_neighbors(
        system,
        neighbors,
        arguments.particle,
        arguments.rc,
        arguments.boundary,
        arguments.figure,
    )
    print(f"Figura escrita en {arguments.figure}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tp1viz",
        description="Visualización y análisis del TP1.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    plot_m_parser = subparsers.add_parser(
        "plot-m",
        help="resume metrics-m.csv y grafica tiempo frente a M",
    )
    plot_m_parser.add_argument(
        "inputs",
        metavar="INPUT.csv",
        nargs="+",
        type=Path,
        help="uno o más CSV producidos por benchmark-m",
    )
    plot_m_parser.add_argument(
        "--summary",
        type=Path,
        required=True,
        help="CSV de salida con promedio y desvío estándar",
    )
    plot_m_parser.add_argument(
        "--figure",
        type=Path,
        required=True,
        help="imagen de salida, por ejemplo time-vs-m.png",
    )
    plot_m_parser.add_argument(
        "--log-x",
        action="store_true",
        help="usa escala logarítmica para M",
    )
    plot_m_parser.add_argument(
        "--log-y",
        action="store_true",
        help="usa escala logarítmica para el tiempo",
    )
    plot_m_parser.set_defaults(handler=_run_plot_m)

    plot_neighbors_parser = subparsers.add_parser(
        "plot-neighbors",
        help="dibuja una partícula y sus vecinas",
    )
    plot_neighbors_parser.add_argument(
        "--static", type=Path, required=True, help="archivo static.txt"
    )
    plot_neighbors_parser.add_argument(
        "--dynamic", type=Path, required=True, help="archivo dynamic.txt"
    )
    plot_neighbors_parser.add_argument(
        "--neighbors", type=Path, required=True, help="archivo neighbors.txt"
    )
    plot_neighbors_parser.add_argument(
        "--particle", type=int, required=True, help="ID de la partícula elegida"
    )
    plot_neighbors_parser.add_argument(
        "--rc", type=float, default=1.0, help="radio de interacción (1)"
    )
    plot_neighbors_parser.add_argument(
        "--boundary",
        choices=("walls", "periodic"),
        default="walls",
        help="tipo de contorno (walls)",
    )
    plot_neighbors_parser.add_argument(
        "--figure", type=Path, required=True, help="imagen de salida"
    )
    plot_neighbors_parser.set_defaults(handler=_run_plot_neighbors)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    if not hasattr(arguments, "handler"):
        parser.print_help()
        return 0
    try:
        return arguments.handler(arguments)
    except (MetricsError, ParticleDataError) as error:
        parser.error(str(error))
