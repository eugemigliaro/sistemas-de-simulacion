"""Lectura y resumen de mediciones de rendimiento del motor."""

from __future__ import annotations

import math
import re
import statistics
from dataclasses import dataclass
from typing import Iterable, Mapping


_FLOAT = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
_SUMMARY = re.compile(
    rf"^engine (?P<engine>\S+)"
    rf" particles (?P<particle_count>\d+)"
    rf" seed (?P<seed>\d+)"
    rf" events (?P<events>\d+)"
    rf" frames (?P<frames>\d+)"
    rf" final_time (?P<final_time>{_FLOAT})"
    rf" runtime_seconds (?P<runtime_seconds>{_FLOAT})$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class EngineReport:
    engine: str
    particle_count: int
    seed: int
    events: int
    frames: int
    final_time: float
    runtime_seconds: float


def parse_engine_report(stderr: str) -> EngineReport:
    """Extrae el único resumen estructurado emitido por el motor."""

    matches = list(_SUMMARY.finditer(stderr))
    if len(matches) != 1:
        raise ValueError(
            "se esperaba exactamente un resumen del motor en stderr; "
            f"se encontraron {len(matches)}"
        )
    values = matches[0].groupdict()
    report = EngineReport(
        engine=values["engine"],
        particle_count=int(values["particle_count"]),
        seed=int(values["seed"]),
        events=int(values["events"]),
        frames=int(values["frames"]),
        final_time=float(values["final_time"]),
        runtime_seconds=float(values["runtime_seconds"]),
    )
    if report.runtime_seconds < 0 or not math.isfinite(report.runtime_seconds):
        raise ValueError("runtime_seconds debe ser finito y no negativo")
    if report.final_time < 0 or not math.isfinite(report.final_time):
        raise ValueError("final_time debe ser finito y no negativo")
    return report


def summarize_performance(
    rows: Iterable[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Agrupa observaciones por motor, N y tiempo final solicitado."""

    groups: dict[tuple[str, int, float], list[tuple[int, float, int, int]]] = {}
    for row in rows:
        engine = row["engine"]
        particle_count = int(row["particle_count"])
        seed = int(row["seed"])
        max_time = float(row["max_time"])
        runtime = float(row["runtime_seconds"])
        events = int(row["events"])
        frames = int(row["frames"])
        if particle_count <= 0 or max_time <= 0 or runtime < 0:
            raise ValueError("observación de rendimiento fuera de rango")
        groups.setdefault((engine, particle_count, max_time), []).append(
            (seed, runtime, events, frames)
        )

    result: list[dict[str, str]] = []
    for (engine, particle_count, max_time), observations in sorted(
        groups.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])
    ):
        seeds = [item[0] for item in observations]
        if len(seeds) != len(set(seeds)):
            raise ValueError(
                f"semillas repetidas para engine={engine}, N={particle_count}"
            )
        runtimes = [item[1] for item in observations]
        events = [item[2] for item in observations]
        frames = [item[3] for item in observations]
        repetitions = len(runtimes)
        runtime_std = statistics.stdev(runtimes) if repetitions > 1 else 0.0
        result.append(
            {
                "engine": engine,
                "particle_count": str(particle_count),
                "max_time": f"{max_time:.17g}",
                "repetitions": str(repetitions),
                "runtime_mean_s": f"{statistics.fmean(runtimes):.17g}",
                "runtime_std_s": f"{runtime_std:.17g}",
                "runtime_sem_s": f"{runtime_std / math.sqrt(repetitions):.17g}",
                "runtime_min_s": f"{min(runtimes):.17g}",
                "runtime_max_s": f"{max(runtimes):.17g}",
                "events_mean": f"{statistics.fmean(events):.17g}",
                "frames_mean": f"{statistics.fmean(frames):.17g}",
            }
        )
    return result
