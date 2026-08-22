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
    particle_count: int = 0
    side: float = 10.0
    cells_per_side: int = 9
    cutoff: float = 1.0
    speed: float = 0.03
    time_step: float = 1.0


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
    particle_count: int = 0
    side: float = 10.0
    cells_per_side: int = 9
    cutoff: float = 1.0
    speed: float = 0.03
    time_step: float = 1.0


OBSERVATION_FIELDS = (
    "model", "density", "particle_count", "side", "cells_per_side",
    "cutoff", "speed", "time_step", "eta", "seed", "time",
    "polarization", "largest_cluster_fraction", "cim_time_ns",
    "neighbor_pairs", "distance_evaluations",
)

TRAJECTORY_FIELDS = (
    "model", "density", "particle_count", "side", "cells_per_side",
    "cutoff", "speed", "time_step", "eta", "seed", "time", "id",
    "x", "y", "vx", "vy", "angle",
)


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
        return int(value)
    except ValueError as error:
        raise ValueError(f"{path}:{line}: {field} inválido") from error


def _rows(
    path: Path,
    accepted: tuple[tuple[str, ...], ...],
) -> tuple[tuple[str, ...], list[tuple[int, dict[str, str]]]]:
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        fields = tuple(reader.fieldnames or ())
        if fields not in accepted:
            raise ValueError(f"{path}: encabezado inesperado")
        rows = [(line, row) for line, row in enumerate(reader, start=2)]
    return fields, rows


def _metadata(
    row: dict[str, str],
    density: float,
    source: Path,
    line: int,
) -> dict[str, int | float]:
    metadata: dict[str, int | float] = {
        "particle_count": _integer(
            row["particle_count"], "particle_count", source, line
        ),
        "side": _finite(row["side"], "side", source, line),
        "cells_per_side": _integer(
            row["cells_per_side"], "cells_per_side", source, line
        ),
        "cutoff": _finite(row["cutoff"], "cutoff", source, line),
        "speed": _finite(row["speed"], "speed", source, line),
        "time_step": _finite(row["time_step"], "time_step", source, line),
    }

    particle_count = int(metadata["particle_count"])
    side = float(metadata["side"])
    cells_per_side = int(metadata["cells_per_side"])
    cutoff = float(metadata["cutoff"])
    speed = float(metadata["speed"])
    time_step = float(metadata["time_step"])
    if (
        particle_count <= 0 or side <= 0 or cells_per_side <= 0
        or cutoff <= 0 or speed <= 0 or time_step <= 0
    ):
        raise ValueError(f"{source}:{line}: metadatos físicos fuera de rango")
    actual_density = particle_count / (side * side)
    if not math.isclose(density, actual_density, abs_tol=1e-12):
        raise ValueError(f"{source}:{line}: densidad incompatible con N y L")
    return metadata


def observation_run_key(row: Observation) -> tuple:
    return (
        row.model, row.density, row.particle_count, row.side,
        row.cells_per_side, row.cutoff, row.speed, row.time_step,
        row.eta, row.seed,
    )


def trajectory_run_key(row: ParticleState) -> tuple:
    return (
        row.model, row.density, row.particle_count, row.side,
        row.cells_per_side, row.cutoff, row.speed, row.time_step,
        row.eta, row.seed,
    )


def read_observations(path: str | Path) -> list[Observation]:
    source = Path(path)
    _fields, source_rows = _rows(source, (OBSERVATION_FIELDS,))
    result: list[Observation] = []
    for line, row in source_rows:
        model = row["model"]
        density = _finite(row["density"], "density", source, line)
        eta = _finite(row["eta"], "eta", source, line)
        time = _finite(row["time"], "time", source, line)
        polarization = _finite(row["polarization"], "polarization", source, line)
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
            row["distance_evaluations"], "distance_evaluations", source, line
        )
        metadata = _metadata(row, density, source, line)
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
                **metadata,
            )
        )
    if not result:
        raise ValueError(f"{source}: no contiene observaciones")
    return result


def read_trajectory(path: str | Path) -> list[ParticleState]:
    source = Path(path)
    _fields, source_rows = _rows(source, (TRAJECTORY_FIELDS,))
    result: list[ParticleState] = []
    for line, row in source_rows:
        density = _finite(row["density"], "density", source, line)
        metadata = _metadata(row, density, source, line)
        state = ParticleState(
            model=row["model"],
            density=density,
            eta=_finite(row["eta"], "eta", source, line),
            seed=_integer(row["seed"], "seed", source, line),
            time=_finite(row["time"], "time", source, line),
            particle_id=_integer(row["id"], "id", source, line),
            x=_finite(row["x"], "x", source, line),
            y=_finite(row["y"], "y", source, line),
            vx=_finite(row["vx"], "vx", source, line),
            vy=_finite(row["vy"], "vy", source, line),
            angle=_finite(row["angle"], "angle", source, line),
            **metadata,
        )
        if state.model not in {"vicsek", "voter"}:
            raise ValueError(f"{source}:{line}: modelo desconocido")
        if (
            state.particle_id <= 0 or not 0 <= state.eta <= 1
            or state.time < 0 or not 0 <= state.x < state.side
            or not 0 <= state.y < state.side
            or not -math.pi <= state.angle < math.pi
        ):
            raise ValueError(f"{source}:{line}: estado fuera de rango")
        if not math.isclose(
            math.hypot(state.vx, state.vy),
            state.speed,
            rel_tol=1e-10,
            abs_tol=1e-12,
        ):
            raise ValueError(f"{source}:{line}: velocidad incompatible con v")
        result.append(state)
    if not result:
        raise ValueError(f"{source}: no contiene partículas")
    return result


def group_frames(states: Iterable[ParticleState]) -> list[tuple[float, list[ParticleState]]]:
    rows = list(states)
    if not rows:
        raise ValueError("no hay estados de partículas")
    expected_key = trajectory_run_key(rows[0])
    frames: list[tuple[float, list[ParticleState]]] = []
    seen_times: set[float] = set()
    for state in rows:
        if trajectory_run_key(state) != expected_key:
            raise ValueError("la trayectoria mezcla corridas diferentes")
        if not frames or state.time != frames[-1][0]:
            if state.time in seen_times or (frames and state.time <= frames[-1][0]):
                raise ValueError("los tiempos de la trayectoria no son crecientes")
            seen_times.add(state.time)
            frames.append((state.time, [state]))
        else:
            frames[-1][1].append(state)
    for time, frame in frames:
        ids = [state.particle_id for state in frame]
        expected_count = frame[0].particle_count or len(frame)
        if ids != list(range(1, expected_count + 1)):
            raise ValueError(f"cuadro t={time:g}: IDs incompletos o desordenados")
    return frames
