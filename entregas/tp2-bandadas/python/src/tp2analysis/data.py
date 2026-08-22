from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Observation:
    model: str
    density: float
    eta: float
    seed: int
    time: float
    polarization: float
    largest_cluster_fraction: float
    cim_time_ns: int
    neighbor_pairs: int
    distance_evaluations: int


@dataclass(frozen=True)
class ParticleState:
    model: str
    density: float
    eta: float
    seed: int
    time: float
    particle_id: int
    x: float
    y: float
    vx: float
    vy: float
    angle: float


def _finite(value: str, field: str, path: Path, line: int) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise ValueError(f"{path}:{line}: {field} inválido") from error
    if not math.isfinite(parsed):
        raise ValueError(f"{path}:{line}: {field} no finito")
    return parsed


def _integer(value: str, field: str, path: Path, line: int) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise ValueError(f"{path}:{line}: {field} inválido") from error
    return parsed


def _rows(path: Path, expected: tuple[str, ...]) -> Iterable[tuple[int, dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != expected:
            raise ValueError(f"{path}: encabezado inesperado")
        for line, row in enumerate(reader, start=2):
            yield line, row


def read_observations(path: str | Path) -> list[Observation]:
    source = Path(path)
    expected = (
        "model",
        "density",
        "eta",
        "seed",
        "time",
        "polarization",
        "largest_cluster_fraction",
        "cim_time_ns",
        "neighbor_pairs",
        "distance_evaluations",
    )
    result: list[Observation] = []
    for line, row in _rows(source, expected):
        model = row["model"]
        density = _finite(row["density"], "density", source, line)
        eta = _finite(row["eta"], "eta", source, line)
        time = _finite(row["time"], "time", source, line)
        polarization = _finite(
            row["polarization"], "polarization", source, line
        )
        cluster = _finite(
            row["largest_cluster_fraction"],
            "largest_cluster_fraction",
            source,
            line,
        )
        seed = _integer(row["seed"], "seed", source, line)
        cim_time = _integer(row["cim_time_ns"], "cim_time_ns", source, line)
        pairs = _integer(row["neighbor_pairs"], "neighbor_pairs", source, line)
        evaluations = _integer(
            row["distance_evaluations"],
            "distance_evaluations",
            source,
            line,
        )
        if model not in {"vicsek", "voter"}:
            raise ValueError(f"{source}:{line}: modelo desconocido")
        if density <= 0 or not 0 <= eta <= 1 or time < 0:
            raise ValueError(f"{source}:{line}: metadatos fuera de rango")
        if not -1e-12 <= polarization <= 1 + 1e-12:
            raise ValueError(f"{source}:{line}: polarización fuera de rango")
        if not 0 < cluster <= 1 + 1e-12:
            raise ValueError(f"{source}:{line}: S fuera de rango")
        if seed < 0 or cim_time < 0 or pairs < 0 or evaluations < 0:
            raise ValueError(f"{source}:{line}: entero negativo")
        result.append(
            Observation(
                model=model,
                density=density,
                eta=eta,
                seed=seed,
                time=time,
                polarization=polarization,
                largest_cluster_fraction=cluster,
                cim_time_ns=cim_time,
                neighbor_pairs=pairs,
                distance_evaluations=evaluations,
            )
        )
    if not result:
        raise ValueError(f"{source}: no contiene observaciones")
    return result


def read_trajectory(path: str | Path) -> list[ParticleState]:
    source = Path(path)
    expected = (
        "model",
        "density",
        "eta",
        "seed",
        "time",
        "id",
        "x",
        "y",
        "vx",
        "vy",
        "angle",
    )
    result: list[ParticleState] = []
    for line, row in _rows(source, expected):
        state = ParticleState(
            model=row["model"],
            density=_finite(row["density"], "density", source, line),
            eta=_finite(row["eta"], "eta", source, line),
            seed=_integer(row["seed"], "seed", source, line),
            time=_finite(row["time"], "time", source, line),
            particle_id=_integer(row["id"], "id", source, line),
            x=_finite(row["x"], "x", source, line),
            y=_finite(row["y"], "y", source, line),
            vx=_finite(row["vx"], "vx", source, line),
            vy=_finite(row["vy"], "vy", source, line),
            angle=_finite(row["angle"], "angle", source, line),
        )
        if state.model not in {"vicsek", "voter"}:
            raise ValueError(f"{source}:{line}: modelo desconocido")
        if state.particle_id <= 0 or not 0 <= state.eta <= 1:
            raise ValueError(f"{source}:{line}: estado fuera de rango")
        result.append(state)
    if not result:
        raise ValueError(f"{source}: no contiene partículas")
    return result


def group_frames(states: Iterable[ParticleState]) -> list[tuple[float, list[ParticleState]]]:
    frames: list[tuple[float, list[ParticleState]]] = []
    for state in states:
        if not frames or state.time != frames[-1][0]:
            frames.append((state.time, [state]))
        else:
            frames[-1][1].append(state)
    for time, frame in frames:
        ids = [state.particle_id for state in frame]
        if ids != list(range(1, len(frame) + 1)):
            raise ValueError(f"cuadro t={time:g}: IDs incompletos o desordenados")
    return frames
