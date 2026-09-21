"""Interfaz de línea de comandos del post-proceso.

Cada comando lee trayectorias del motor y escribe tablas CSV; ninguno corre
la simulación. Los gráficos se arman sobre estas tablas.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Iterable, Sequence

from .diffusion import summarize_diffusion
from .goals import T90Result, goal_curve, time_to_fraction
from .msd import MsdCurve, trajectory_msd
from .stats import describe
from .trajectory import Header, read_trajectory


def _write_csv(path: Path, fields: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(fields)
        writer.writerows(rows)


def _check_realizations(headers: list[Header], sources: list[str]) -> None:
    """Las realizaciones a promediar son del mismo sistema y son independientes."""
    first = headers[0]
    for header, source in zip(headers[1:], sources[1:]):
        if header.system_key() != first.system_key():
            raise ValueError(f"{source}: sistema distinto al de {sources[0]}")
    seeds = [header.seed for header in headers]
    if len(set(seeds)) != len(seeds):
        raise ValueError("hay semillas repetidas: las realizaciones no son independientes")


def _format(value: float) -> str:
    return "nan" if math.isnan(value) else f"{value:.6g}"


def command_t90(arguments: argparse.Namespace) -> int:
    results: list[T90Result] = []
    headers: list[Header] = []
    for path in arguments.trajectories:
        trajectory = read_trajectory(path)
        headers.append(trajectory.header)
        results.append(time_to_fraction(trajectory, arguments.fraction))
    _check_realizations(headers, [str(path) for path in arguments.trajectories])

    horizons = {header.max_time for header in headers}
    if len(horizons) > 1:
        raise ValueError("las realizaciones usan distintos tmax")

    if arguments.output:
        _write_csv(
            arguments.output,
            ("source", "seed", "particle_count", "fraction", "threshold_goals",
             "reached", "t90", "final_time", "goals_at_end", "ended_by"),
            (
                (r.source, r.seed, r.particle_count, r.fraction, r.threshold_goals,
                 int(r.reached), "" if r.t90 is None else r.t90, r.final_time,
                 r.goals_at_end, r.ended_by)
                for r in results
            ),
        )

    reached = [r for r in results if r.reached]
    missing = [r for r in results if not r.reached]
    print(f"realizaciones {len(results)}  alcanzaron {len(reached)}")
    if reached:
        t90 = describe(r.t90 for r in reached if r.t90 is not None)
        print(f"<t90> {_format(t90.mean)} s  desvío {_format(t90.std)}  "
              f"error estándar {_format(t90.sem)}  (sobre {t90.count})")
    if missing:
        # Se reportan, no se descartan [TP03, p. 3].
        seeds = ", ".join(str(r.seed) for r in missing)
        print(f"no alcanzaron Fu = {arguments.fraction}: semillas {seeds}")
        truncated = [r for r in missing if r.ended_by == "max_events"]
        if truncated:
            print("aviso: hay corridas cortadas por el tope de eventos, no por tmax")
    goals = describe(r.goals_at_end for r in results)
    print(f"<goles al final> {_format(goals.mean)}  desvío {_format(goals.std)}  "
          f"error estándar {_format(goals.sem)}")
    return 0


def command_goals(arguments: argparse.Namespace) -> int:
    curve = goal_curve(read_trajectory(arguments.trajectory))
    rows = [
        (time, goals, goals / curve.particle_count)
        for time, goals in zip(curve.times.tolist(), curve.goals.tolist())
    ]
    # Cierra el escalón hasta el final de la corrida, para graficar.
    rows.append((curve.end_time, int(curve.goals[-1]), curve.goals[-1] / curve.particle_count))
    _write_csv(arguments.output, ("time", "goals", "used_fraction"), rows)
    return 0


def command_diffusion(arguments: argparse.Namespace) -> int:
    window = (arguments.window[0], arguments.window[1])
    max_lag = arguments.max_lag if arguments.max_lag is not None else window[1]
    if max_lag < window[1]:
        raise ValueError("max-lag debe cubrir la ventana de ajuste")

    curves: list[MsdCurve] = []
    headers: list[Header] = []
    for path in arguments.trajectories:
        trajectory = read_trajectory(path)
        headers.append(trajectory.header)
        curves.append(trajectory_msd(
            trajectory, arguments.bin_width, max_lag, arguments.start_time
        ))
    _check_realizations(headers, [str(path) for path in arguments.trajectories])

    summary = summarize_diffusion(curves, window)
    output = arguments.output_dir

    for header, curve, fit in zip(headers, curves, summary.per_run):
        _write_csv(
            output / f"msd_seed{header.seed}.csv",
            ("lag", "msd", "pairs"),
            zip(curve.lags.tolist(), curve.msd.tolist(), curve.pairs.tolist()),
        )
        _write_csv(
            output / f"ec_seed{header.seed}.csv",
            ("c", "error"),
            zip(fit.fit.sweep_c.tolist(), fit.fit.sweep_error.tolist()),
        )

    pooled = summary.pooled_curve
    _write_csv(
        output / "msd_pooled.csv",
        ("lag", "msd", "std"),
        zip(pooled.lags.tolist(), pooled.msd.tolist(), pooled.std.tolist()),
    )
    _write_csv(
        output / "ec_pooled.csv",
        ("c", "error"),
        zip(summary.pooled.fit.sweep_c.tolist(), summary.pooled.fit.sweep_error.tolist()),
    )

    rows: list[tuple[object, ...]] = [
        ("run", header.seed, fit.coefficient, fit.error, fit.fit.points)
        for header, fit in zip(headers, summary.per_run)
    ]
    rows += [
        ("mean_std", "", summary.plain.mean, summary.plain.std, summary.plain.count),
        ("mean_sem", "", summary.plain.mean, summary.plain.sem, summary.plain.count),
        ("weighted", "", summary.weighted.mean, summary.weighted.error, summary.weighted.count),
        ("pooled", "", summary.pooled.coefficient, summary.pooled.error, summary.pooled.fit.points),
    ]
    _write_csv(
        output / "diffusion.csv",
        ("estimate", "seed", "D", "D_error", "count"),
        rows,
    )

    print(f"ventana [{window[0]}, {window[1]}] s  realizaciones {len(curves)}")
    print(f"media ± desvío          {_format(summary.plain.mean)} ± {_format(summary.plain.std)} m²/s")
    print(f"media ± error estándar  {_format(summary.plain.mean)} ± {_format(summary.plain.sem)} m²/s")
    print(f"media ponderada         {_format(summary.weighted.mean)} ± {_format(summary.weighted.error)} m²/s")
    print(f"ajuste conjunto         {_format(summary.pooled.coefficient)} ± {_format(summary.pooled.error)} m²/s")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tp3analysis",
        description="Post-proceso del TP3: observables sobre la trayectoria del motor.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    t90 = commands.add_parser("t90", help="t90 por realización y su promedio")
    t90.add_argument("trajectories", nargs="+", type=Path)
    t90.add_argument("--fraction", type=float, default=0.9)
    t90.add_argument("--output", type=Path, help="CSV con una fila por realización")
    t90.set_defaults(handler=command_t90)

    goals = commands.add_parser("goals", help="Ng(t) y Fu(t) de una realización")
    goals.add_argument("trajectory", type=Path)
    goals.add_argument("--output", type=Path, required=True)
    goals.set_defaults(handler=command_goals)

    diffusion = commands.add_parser("diffusion", help="DCM y coeficiente de difusión")
    diffusion.add_argument("trajectories", nargs="+", type=Path)
    diffusion.add_argument("--window", type=float, nargs=2, required=True,
                           metavar=("T_A", "T_B"), help="ventana del ajuste en segundos")
    diffusion.add_argument("--bin-width", type=float, default=0.02,
                           help="ancho de los intervalos de desfasaje en segundos")
    diffusion.add_argument("--max-lag", type=float,
                           help="mayor desfasaje a calcular (default: fin de la ventana)")
    diffusion.add_argument("--start-time", type=float, default=0.0,
                           help="descarta orígenes anteriores a este tiempo")
    diffusion.add_argument("--output-dir", type=Path, required=True)
    diffusion.set_defaults(handler=command_diffusion)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        return arguments.handler(arguments)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
