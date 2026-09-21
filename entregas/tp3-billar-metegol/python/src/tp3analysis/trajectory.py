"""Lectura y validación de la trayectoria que escribe el motor.

El motor escribe únicamente estado: tiempo, posiciones, velocidades y color
[TP03, p. 2]. Este módulo lo carga tal cual, sin calcular observables, y
rechaza archivos que no respeten las invariantes del formato para que ningún
análisis corra en silencio sobre datos rotos.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


FORMAT_TAG = "tp3-trajectory"
FORMAT_VERSION = 1
FRAME_REASONS = ("initial", "periodic", "color", "final")


@dataclass(frozen=True)
class Obstacle:
    x: float
    y: float
    radius: float


@dataclass(frozen=True)
class Header:
    length: float
    width: float
    goal_width: float
    particle_count: int
    particle_radius: float
    particle_mass: float
    initial_speed: float
    seed: int
    save_every: int
    obstacles: tuple[Obstacle, ...]
    # Solo los escribe simulate. No son parámetros físicos: sirven para saber
    # por qué terminó la corrida.
    max_time: float | None = None
    max_events: int | None = None

    def system_key(self) -> tuple:
        """Parámetros físicos del sistema [COR02].

        Dos realizaciones son del mismo sistema si coinciden en esto; la
        semilla, la cadencia de guardado y los topes no cuentan.
        """
        return (
            self.length, self.width, self.goal_width, self.particle_count,
            self.particle_radius, self.particle_mass, self.initial_speed,
            self.obstacles,
        )


@dataclass(frozen=True)
class Trajectory:
    header: Header
    times: np.ndarray        # (F,)
    events: np.ndarray       # (F,) eventos procesados al guardar el cuadro
    reasons: tuple[str, ...]
    positions: np.ndarray    # (F, N, 2)
    velocities: np.ndarray   # (F, N, 2)
    states: np.ndarray       # (F, N) 0 fresca, 1 usada
    source: Path | None = None

    @property
    def complete(self) -> bool:
        """El archivo termina en el cuadro final que escribe el motor."""
        return bool(self.reasons) and self.reasons[-1] == "final"

    @property
    def final_time(self) -> float:
        return float(self.times[-1])

    @property
    def reached_max_time(self) -> bool | None:
        """True si la corrida llegó a tmax; None si no puede saberse."""
        if not self.complete or self.header.max_time is None:
            return None
        return math.isclose(
            self.final_time, self.header.max_time, rel_tol=1e-9, abs_tol=1e-12
        )


_HEADER_FLOATS = {
    "length", "width", "goal_width", "particle_radius", "particle_mass",
    "initial_speed", "max_time",
}
_HEADER_INTS = {"particle_count", "seed", "save_every", "obstacle_count", "max_events"}
_HEADER_REQUIRED = {
    "length", "width", "goal_width", "particle_count", "particle_radius",
    "particle_mass", "initial_speed", "seed", "save_every", "obstacle_count",
}


def _parse_header(lines: list[str], source: str) -> tuple[Header, int]:
    if not lines or lines[0].strip() != f"# {FORMAT_TAG} {FORMAT_VERSION}":
        raise ValueError(f"{source}: no es una trayectoria {FORMAT_TAG} {FORMAT_VERSION}")

    values: dict[str, float | int] = {}
    obstacles: list[Obstacle] = []
    columns_seen = False
    index = 1
    while index < len(lines) and lines[index].startswith("#"):
        parts = lines[index][1:].split()
        line = index + 1
        index += 1
        if not parts:
            continue
        key, rest = parts[0], parts[1:]
        try:
            if key == "obstacle":
                x, y, radius = (float(value) for value in rest)
                obstacles.append(Obstacle(x, y, radius))
            elif key == "frame_columns":
                if rest != ["x", "y", "vx", "vy", "state"]:
                    raise ValueError("columnas inesperadas")
                columns_seen = True
            elif key in _HEADER_FLOATS:
                (value,) = rest
                values[key] = float(value)
            elif key in _HEADER_INTS:
                (value,) = rest
                values[key] = int(value)
        except ValueError as error:
            raise ValueError(f"{source}:{line}: cabecera inválida") from error

    missing = _HEADER_REQUIRED - values.keys()
    if missing:
        raise ValueError(f"{source}: faltan en la cabecera {sorted(missing)}")
    if not columns_seen:
        raise ValueError(f"{source}: falta frame_columns en la cabecera")
    if values["obstacle_count"] != len(obstacles):
        raise ValueError(f"{source}: obstacle_count no coincide con los obstáculos")
    if values["particle_count"] <= 0:
        raise ValueError(f"{source}: particle_count debe ser positivo")

    header = Header(
        length=float(values["length"]),
        width=float(values["width"]),
        goal_width=float(values["goal_width"]),
        particle_count=int(values["particle_count"]),
        particle_radius=float(values["particle_radius"]),
        particle_mass=float(values["particle_mass"]),
        initial_speed=float(values["initial_speed"]),
        seed=int(values["seed"]),
        save_every=int(values["save_every"]),
        obstacles=tuple(obstacles),
        max_time=float(values["max_time"]) if "max_time" in values else None,
        max_events=int(values["max_events"]) if "max_events" in values else None,
    )
    return header, index


def parse_trajectory(text: str, source: str = "<texto>") -> Trajectory:
    lines = text.splitlines()
    header, index = _parse_header(lines, source)
    count = header.particle_count

    times: list[float] = []
    events: list[int] = []
    reasons: list[str] = []
    data_lines: list[str] = []

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        parts = line.split()
        if parts[0] != "frame" or len(parts) != 5:
            raise ValueError(f"{source}:{index + 1}: se esperaba un encabezado de cuadro")
        if int(parts[1]) != len(times):
            raise ValueError(f"{source}:{index + 1}: índice de cuadro fuera de secuencia")
        if parts[4] not in FRAME_REASONS:
            raise ValueError(f"{source}:{index + 1}: motivo de cuadro desconocido")
        if reasons and reasons[-1] == "final":
            raise ValueError(f"{source}:{index + 1}: hay cuadros después del final")
        body = lines[index + 1:index + 1 + count]
        if len(body) != count or any(row.startswith("frame") for row in body):
            raise ValueError(f"{source}:{index + 1}: cuadro incompleto")
        times.append(float(parts[2]))
        events.append(int(parts[3]))
        reasons.append(parts[4])
        data_lines.extend(body)
        index += 1 + count

    if not times:
        raise ValueError(f"{source}: la trayectoria no tiene cuadros")

    try:
        raw = np.array(" ".join(data_lines).split(), dtype=float)
        raw = raw.reshape(len(times), count, 5)
    except ValueError as error:
        raise ValueError(f"{source}: cada partícula debe tener 5 columnas") from error

    time_array = np.array(times)
    event_array = np.array(events, dtype=np.int64)
    states = raw[:, :, 4]

    if reasons[0] != "initial" or time_array[0] != 0.0:
        raise ValueError(f"{source}: el primer cuadro debe ser el inicial en t = 0")
    if "initial" in reasons[1:]:
        raise ValueError(f"{source}: hay más de un cuadro inicial")
    if not np.all(np.isfinite(raw)) or not np.all(np.isfinite(time_array)):
        raise ValueError(f"{source}: valores no finitos")
    if np.any(np.diff(time_array) < 0) or np.any(np.diff(event_array) < 0):
        raise ValueError(f"{source}: el tiempo o los eventos retroceden")
    if not np.all((states == 0) | (states == 1)):
        raise ValueError(f"{source}: el estado debe ser 0 o 1")
    # Una partícula usada nunca vuelve a ser fresca [TP03, p. 2].
    if np.any(np.diff(states, axis=0) < 0):
        raise ValueError(f"{source}: una partícula usada volvió a ser fresca")

    return Trajectory(
        header=header,
        times=time_array,
        events=event_array,
        reasons=tuple(reasons),
        positions=raw[:, :, 0:2].copy(),
        velocities=raw[:, :, 2:4].copy(),
        states=states.astype(np.int8),
        source=Path(source) if source != "<texto>" else None,
    )


def read_trajectory(path: str | Path) -> Trajectory:
    source = Path(path)
    return parse_trajectory(source.read_text(encoding="utf-8"), str(source))
