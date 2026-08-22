from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping

from .data import Observation, observation_run_key


StationaryKey = tuple[str, float, float]
StationaryStarts = Mapping[StationaryKey, float]


@dataclass(frozen=True)
class Summary:
    model: str
    density: float
    eta: float
    realizations: int
    stationary_start: float
    polarization_mean: float
    polarization_std: float
    cluster_mean: float
    cluster_std: float
    cim_time_ns_mean: float
    particle_count: int = 0
    side: float = 10.0
    cells_per_side: int = 9
    cutoff: float = 1.0
    speed: float = 0.03
    time_step: float = 1.0


@dataclass(frozen=True)
class BlockSummary:
    model: str
    density: float
    eta: float
    seed: int
    block_start: float
    block_end: float
    samples: int
    polarization_mean: float
    polarization_std: float
    cluster_mean: float
    cluster_std: float


SUMMARY_FIELDS = (
    "model", "density", "particle_count", "side", "cells_per_side",
    "cutoff", "speed", "time_step", "eta", "realizations",
    "stationary_start", "polarization_mean", "polarization_std",
    "cluster_mean", "cluster_std", "cim_time_ns_mean",
)

BLOCK_FIELDS = (
    "model", "density", "eta", "seed", "block_start", "block_end",
    "samples", "polarization_mean", "polarization_std", "cluster_mean",
    "cluster_std",
)

STATIONARY_START_FIELDS = ("model", "density", "eta", "stationary_start")


def _mean(values: list[float]) -> float:
    if not values:
        raise ValueError("no hay valores para promediar")
    return statistics.fmean(values)


def _std(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def _parameter_key(row: Observation) -> tuple:
    return observation_run_key(row)[:-1]


def _validated_runs(
    observations: Iterable[Observation],
) -> dict[tuple, list[Observation]]:
    grouped: dict[tuple, list[Observation]] = defaultdict(list)
    for observation in observations:
        grouped[observation_run_key(observation)].append(observation)
    if not grouped:
        raise ValueError("no hay observaciones")
    for key, rows in grouped.items():
        rows.sort(key=lambda row: row.time)
        times = [row.time for row in rows]
        if len(times) != len(set(times)):
            raise ValueError(f"corrida duplicada o tiempos repetidos: {key}")
        if any(second <= first for first, second in zip(times, times[1:])):
            raise ValueError(f"tiempos no crecientes: {key}")
    return grouped


def read_stationary_starts(path: str | Path) -> dict[StationaryKey, float]:
    source = Path(path)
    result: dict[StationaryKey, float] = {}
    with source.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        if tuple(reader.fieldnames or ()) != STATIONARY_START_FIELDS:
            raise ValueError(f"{source}: encabezado de descartes inesperado")
        for line, row in enumerate(reader, start=2):
            try:
                key = (row["model"], float(row["density"]), float(row["eta"]))
                start = float(row["stationary_start"])
            except ValueError as error:
                raise ValueError(f"{source}:{line}: valor inválido") from error
            if key[0] not in {"vicsek", "voter"} or start < 0 or not math.isfinite(start):
                raise ValueError(f"{source}:{line}: descarte fuera de rango")
            if key in result:
                raise ValueError(f"{source}:{line}: descarte duplicado")
            result[key] = start
    if not result:
        raise ValueError(f"{source}: tabla de descartes vacía")
    return result


def _start_for(
    row: Observation,
    stationary_start: float | StationaryStarts,
) -> float:
    if isinstance(stationary_start, (int, float)):
        start = float(stationary_start)
    else:
        key = (row.model, row.density, row.eta)
        if key not in stationary_start:
            raise ValueError(f"falta inicio estacionario para {key}")
        start = float(stationary_start[key])
    if start < 0 or not math.isfinite(start):
        raise ValueError("stationary_start debe ser finito y no negativo")
    return start


def summarize(
    observations: Iterable[Observation],
    stationary_start: float | StationaryStarts,
) -> list[Summary]:
    runs = _validated_runs(observations)
    filtered: dict[tuple, list[Observation]] = {}
    for run_key, rows in runs.items():
        start = _start_for(rows[0], stationary_start)
        selected = [row for row in rows if row.time >= start]
        if len(selected) < 2:
            raise ValueError(f"corrida sin suficientes muestras estacionarias: {run_key}")
        filtered[run_key] = selected

    by_parameter: dict[tuple, list[list[Observation]]] = defaultdict(list)
    for rows in filtered.values():
        by_parameter[_parameter_key(rows[0])].append(rows)

    summaries: list[Summary] = []
    for parameter, realizations in sorted(by_parameter.items()):
        signatures = {(len(rows), rows[0].time, rows[-1].time) for rows in realizations}
        if len(signatures) != 1:
            raise ValueError(f"corridas truncadas o de distinta duración: {parameter}")
        first = realizations[0][0]
        polarization_means = [
            _mean([row.polarization for row in rows]) for rows in realizations
        ]
        cluster_means = [
            _mean([row.largest_cluster_fraction for row in rows])
            for rows in realizations
        ]
        cim_means = [
            _mean([float(row.cim_time_ns) for row in rows]) for rows in realizations
        ]
        summaries.append(
            Summary(
                model=first.model,
                density=first.density,
                eta=first.eta,
                realizations=len(realizations),
                stationary_start=_start_for(first, stationary_start),
                polarization_mean=_mean(polarization_means),
                polarization_std=_std(polarization_means),
                cluster_mean=_mean(cluster_means),
                cluster_std=_std(cluster_means),
                cim_time_ns_mean=_mean(cim_means),
                particle_count=first.particle_count,
                side=first.side,
                cells_per_side=first.cells_per_side,
                cutoff=first.cutoff,
                speed=first.speed,
                time_step=first.time_step,
            )
        )
    return summaries


def block_summaries(
    observations: Iterable[Observation],
    block_size: float,
    start: float = 0.0,
) -> list[BlockSummary]:
    if block_size <= 0 or start < 0 or not math.isfinite(block_size + start):
        raise ValueError("block_size debe ser positivo y start no negativo")
    result: list[BlockSummary] = []
    for rows in _validated_runs(observations).values():
        blocks: dict[int, list[Observation]] = defaultdict(list)
        for row in rows:
            if row.time >= start:
                index = int(math.floor((row.time - start) / block_size))
                blocks[index].append(row)
        if not blocks:
            raise ValueError("ninguna observación pertenece a los bloques")
        samples_per_block = block_size / rows[0].time_step
        expected_samples = round(samples_per_block)
        if expected_samples < 1 or not math.isclose(
            samples_per_block,
            expected_samples,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            raise ValueError("block_size debe ser un múltiplo entero de dt")
        for index, values in sorted(blocks.items()):
            if len(values) < expected_samples:
                continue
            first = values[0]
            result.append(
                BlockSummary(
                    model=first.model,
                    density=first.density,
                    eta=first.eta,
                    seed=first.seed,
                    block_start=start + index * block_size,
                    block_end=start + (index + 1) * block_size,
                    samples=len(values),
                    polarization_mean=_mean([row.polarization for row in values]),
                    polarization_std=_std([row.polarization for row in values]),
                    cluster_mean=_mean(
                        [row.largest_cluster_fraction for row in values]
                    ),
                    cluster_std=_std(
                        [row.largest_cluster_fraction for row in values]
                    ),
                )
            )
    if not result:
        raise ValueError("no hay bloques temporales completos")
    return sorted(
        result,
        key=lambda row: (row.model, row.density, row.eta, row.seed, row.block_start),
    )


def write_blocks(path: str | Path, blocks: Iterable[BlockSummary]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=BLOCK_FIELDS)
        writer.writeheader()
        for block in blocks:
            writer.writerow(asdict(block))


def write_summaries(path: str | Path, summaries: Iterable[Summary]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for summary in summaries:
            row = asdict(summary)
            writer.writerow({field: row[field] for field in SUMMARY_FIELDS})


def read_summaries(path: str | Path) -> list[Summary]:
    source = Path(path)
    result: list[Summary] = []
    with source.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        fields = tuple(reader.fieldnames or ())
        if fields != SUMMARY_FIELDS:
            raise ValueError(f"{source}: encabezado de resumen inesperado")
        for row in reader:
            metadata = {
                "particle_count": int(row["particle_count"]),
                "side": float(row["side"]),
                "cells_per_side": int(row["cells_per_side"]),
                "cutoff": float(row["cutoff"]),
                "speed": float(row["speed"]),
                "time_step": float(row["time_step"]),
            }
            result.append(
                Summary(
                    model=row["model"],
                    density=float(row["density"]),
                    eta=float(row["eta"]),
                    realizations=int(row["realizations"]),
                    stationary_start=float(row["stationary_start"]),
                    polarization_mean=float(row["polarization_mean"]),
                    polarization_std=float(row["polarization_std"]),
                    cluster_mean=float(row["cluster_mean"]),
                    cluster_std=float(row["cluster_std"]),
                    cim_time_ns_mean=float(row["cim_time_ns_mean"]),
                    **metadata,
                )
            )
    if not result:
        raise ValueError(f"{source}: resumen vacío")
    return result
