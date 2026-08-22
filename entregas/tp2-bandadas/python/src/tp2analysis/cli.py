from __future__ import annotations

import argparse
from pathlib import Path

from . import __version__
from .animation import animate
from .cim import (
    plot_cim_comparison,
    read_cim_summaries,
    summarize_cim,
    write_cim_summaries,
)
from .data import read_observations, read_trajectory
from .plotting import (
    plot_blocks,
    plot_eta,
    plot_polarization_vs_cluster,
    plot_time_series,
)
from .stats import (
    block_summaries,
    read_stationary_starts,
    read_summaries,
    summarize,
    write_blocks,
    write_summaries,
)


def _stationary_options(parser: argparse.ArgumentParser, required: bool) -> None:
    group = parser.add_mutually_exclusive_group(required=required)
    group.add_argument("--stationary-start", type=float)
    group.add_argument("--stationary-starts", type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tp2analysis")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    summary = commands.add_parser("summary")
    summary.add_argument("inputs", nargs="+", type=Path)
    _stationary_options(summary, required=True)
    summary.add_argument("--output", required=True, type=Path)

    timeseries = commands.add_parser("timeseries")
    timeseries.add_argument("inputs", nargs="+", type=Path)
    timeseries.add_argument("--output", required=True, type=Path)
    _stationary_options(timeseries, required=False)

    blocks = commands.add_parser("blocks")
    blocks.add_argument("inputs", nargs="+", type=Path)
    blocks.add_argument("--block-size", required=True, type=float)
    blocks.add_argument("--start", default=0.0, type=float)
    blocks.add_argument("--output", required=True, type=Path)
    blocks.add_argument("--plot", type=Path)

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
    animation.add_argument("--observables", required=True, type=Path)
    animation.add_argument("--output", required=True, type=Path)
    animation.add_argument("--L", type=float)
    animation.add_argument("--fps", type=float, default=5.0)

    cim_summary = commands.add_parser("cim-summary")
    cim_summary.add_argument("inputs", nargs="+", type=Path)
    cim_summary.add_argument("--start", default=0.0, type=float)
    cim_summary.add_argument("--output", required=True, type=Path)

    cim_plot = commands.add_parser("plot-cim")
    cim_plot.add_argument("--input", required=True, type=Path)
    cim_plot.add_argument("--tp1", required=True, type=Path)
    cim_plot.add_argument("--output", required=True, type=Path)
    return parser


def _read_all_observations(paths: list[Path]):
    observations = []
    for path in paths:
        observations.extend(read_observations(path))
    return observations


def _stationary_value(arguments: argparse.Namespace):
    if getattr(arguments, "stationary_starts", None) is not None:
        return read_stationary_starts(arguments.stationary_starts)
    return getattr(arguments, "stationary_start", None)


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "summary":
        write_summaries(
            arguments.output,
            summarize(
                _read_all_observations(arguments.inputs),
                _stationary_value(arguments),
            ),
        )
    elif arguments.command == "timeseries":
        plot_time_series(
            _read_all_observations(arguments.inputs),
            arguments.output,
            _stationary_value(arguments),
        )
    elif arguments.command == "blocks":
        blocks = block_summaries(
            _read_all_observations(arguments.inputs),
            arguments.block_size,
            arguments.start,
        )
        write_blocks(arguments.output, blocks)
        if arguments.plot is not None:
            plot_blocks(blocks, arguments.plot)
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
            read_observations(arguments.observables),
            arguments.output,
            arguments.L,
            arguments.fps,
        )
    elif arguments.command == "cim-summary":
        write_cim_summaries(
            arguments.output,
            summarize_cim(
                _read_all_observations(arguments.inputs),
                arguments.start,
            ),
        )
    elif arguments.command == "plot-cim":
        plot_cim_comparison(
            read_cim_summaries(arguments.input),
            arguments.tp1,
            arguments.output,
        )
    return 0
