"""Lectura validada de sistemas de partículas y listas de vecinos."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path


class ParticleDataError(ValueError):
    """Indica que un archivo del sistema no respeta el contrato del TP1."""


@dataclass(frozen=True)
class Particle:
    id: int
    radius: float
    property: float
    x: float
    y: float
    vx: float
    vy: float


@dataclass(frozen=True)
class ParticleSystem:
    side: float
    time: float
    particles: tuple[Particle, ...]


def _read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ParticleDataError(f"no se pudo leer {path}: {error}") from error


def _parse_float(token: str, location: str) -> float:
    try:
        value = float(token)
    except ValueError as error:
        raise ParticleDataError(f"{location}: se esperaba un número real") from error
    if not math.isfinite(value):
        raise ParticleDataError(f"{location}: el valor debe ser finito")
    return value


def _parse_row(line: str, counts: set[int], location: str) -> list[float]:
    tokens = line.split()
    if len(tokens) not in counts:
        expected = " o ".join(str(count) for count in sorted(counts))
        raise ParticleDataError(
            f"{location}: se esperaban {expected} columnas"
        )
    return [
        _parse_float(token, f"{location}, columna {index}")
        for index, token in enumerate(tokens, start=1)
    ]


def read_system(static_path: Path, dynamic_path: Path) -> ParticleSystem:
    """Lee un único estado en los formatos estático y dinámico oficiales."""

    static_lines = _read_lines(static_path)
    dynamic_lines = _read_lines(dynamic_path)
    if len(static_lines) < 2:
        raise ParticleDataError(f"{static_path}: faltan los encabezados N y L")

    try:
        particle_count = int(static_lines[0])
    except ValueError as error:
        raise ParticleDataError(
            f"{static_path}:1: N debe ser un entero positivo"
        ) from error
    if particle_count <= 0:
        raise ParticleDataError(f"{static_path}:1: N debe ser positivo")
    if len(static_lines) != particle_count + 2:
        raise ParticleDataError(
            f"{static_path}: se esperaban {particle_count} filas de partículas"
        )

    side = _parse_row(static_lines[1], {1}, f"{static_path}:2")[0]
    if side <= 0:
        raise ParticleDataError(f"{static_path}:2: L debe ser positivo")

    if len(dynamic_lines) != particle_count + 1:
        raise ParticleDataError(
            f"{dynamic_path}: se esperaban {particle_count} filas de partículas"
        )
    time = _parse_row(dynamic_lines[0], {1}, f"{dynamic_path}:1")[0]

    particles: list[Particle] = []
    for index in range(particle_count):
        static_row = _parse_row(
            static_lines[index + 2],
            {2},
            f"{static_path}:{index + 3}",
        )
        dynamic_row = _parse_row(
            dynamic_lines[index + 1],
            {2, 4},
            f"{dynamic_path}:{index + 2}",
        )
        radius, property_value = static_row
        if radius <= 0:
            raise ParticleDataError(
                f"{static_path}:{index + 3}: el radio debe ser positivo"
            )
        x, y = dynamic_row[:2]
        if not 0 <= x <= side or not 0 <= y <= side:
            raise ParticleDataError(
                f"{dynamic_path}:{index + 2}: posición fuera del dominio"
            )
        vx, vy = dynamic_row[2:] if len(dynamic_row) == 4 else (0.0, 0.0)
        particles.append(
            Particle(
                id=index + 1,
                radius=radius,
                property=property_value,
                x=x,
                y=y,
                vx=vx,
                vy=vy,
            )
        )

    return ParticleSystem(side=side, time=time, particles=tuple(particles))


def read_neighbors(path: Path, particle_count: int) -> tuple[frozenset[int], ...]:
    """Lee y valida una lista simétrica, completa y sin duplicados."""

    lines = _read_lines(path)
    if len(lines) != particle_count:
        raise ParticleDataError(
            f"{path}: se esperaban {particle_count} filas de vecinos"
        )

    result: list[frozenset[int]] = []
    for index, line in enumerate(lines, start=1):
        tokens = line.split(",")
        try:
            identifiers = [int(token) for token in tokens]
        except ValueError as error:
            raise ParticleDataError(
                f"{path}:{index}: todos los identificadores deben ser enteros"
            ) from error
        if not identifiers or identifiers[0] != index:
            raise ParticleDataError(
                f"{path}:{index}: la fila debe comenzar con el ID {index}"
            )
        neighbor_ids = identifiers[1:]
        if neighbor_ids != sorted(neighbor_ids) or len(neighbor_ids) != len(
            set(neighbor_ids)
        ):
            raise ParticleDataError(
                f"{path}:{index}: los vecinos deben estar ordenados y sin duplicados"
            )
        if any(
            neighbor_id <= 0
            or neighbor_id > particle_count
            or neighbor_id == index
            for neighbor_id in neighbor_ids
        ):
            raise ParticleDataError(
                f"{path}:{index}: contiene un identificador de vecino inválido"
            )
        result.append(frozenset(neighbor_ids))

    for particle_id, neighbor_ids in enumerate(result, start=1):
        for neighbor_id in neighbor_ids:
            if particle_id not in result[neighbor_id - 1]:
                raise ParticleDataError(
                    f"{path}: la relación {particle_id},{neighbor_id} no es simétrica"
                )
    return tuple(result)
