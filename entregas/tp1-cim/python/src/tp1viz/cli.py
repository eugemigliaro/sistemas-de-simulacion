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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    if not hasattr(arguments, "handler"):
        parser.print_help()
        return 0
    try:
        return arguments.handler(arguments)
    except MetricsError as error:
        parser.error(str(error))
