from __future__ import annotations

import argparse
from pathlib import Path

from . import __version__
from .animation import animate
from .data import read_observations, read_trajectory
from .plotting import plot_eta, plot_polarization_vs_cluster, plot_time_series
from .stats import read_summaries, summarize, write_summaries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tp2analysis")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    summary = commands.add_parser("summary")
    summary.add_argument("inputs", nargs="+", type=Path)
    summary.add_argument("--stationary-start", required=True, type=float)
    summary.add_argument("--output", required=True, type=Path)

    timeseries = commands.add_parser("timeseries")
    timeseries.add_argument("--input", required=True, type=Path)
    timeseries.add_argument("--output", required=True, type=Path)
    timeseries.add_argument("--stationary-start", type=float)

    eta = commands.add_parser("plot-eta")
    eta.add_argument("--input", required=True, type=Path)
    eta.add_argument("--output", required=True, type=Path)
    eta.add_argument(
        "--observable",
        required=True,
        choices=("polarization", "cluster"),
    )

    va_s = commands.add_parser("plot-va-s")
    va_s.add_argument("--input", required=True, type=Path)
    va_s.add_argument("--output", required=True, type=Path)

    animation = commands.add_parser("animate")
    animation.add_argument("--input", required=True, type=Path)
    animation.add_argument("--output", required=True, type=Path)
    animation.add_argument("--L", type=float, default=10.0)
    animation.add_argument("--fps", type=int, default=20)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "summary":
        observations = []
        for path in arguments.inputs:
            observations.extend(read_observations(path))
        write_summaries(
            arguments.output,
            summarize(observations, arguments.stationary_start),
        )
    elif arguments.command == "timeseries":
        plot_time_series(
            read_observations(arguments.input),
            arguments.output,
            arguments.stationary_start,
        )
    elif arguments.command == "plot-eta":
        plot_eta(
            read_summaries(arguments.input),
            arguments.output,
            arguments.observable,
        )
    elif arguments.command == "plot-va-s":
        plot_polarization_vs_cluster(
            read_summaries(arguments.input),
            arguments.output,
        )
    elif arguments.command == "animate":
        animate(
            read_trajectory(arguments.input),
            arguments.output,
            arguments.L,
            arguments.fps,
        )
    return 0
