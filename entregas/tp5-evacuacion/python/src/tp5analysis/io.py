"""Lectura de las salidas del motor (`tp5 evacuate`).

Formato (ver cpp/include/tp5/output.hpp):
    # clave valor clave valor ...      cabecera con los parámetros
    agent <id> <radio> <masa>
    frame <t> <adentro>                seguido de <id> <x> <y> <vx> <vy> <modo>
    exit <t> <id>
    mode <t> <id> <modo>               0 = TSDMD, 1 = EDMD
    # end_time ... wall_seconds ...    pie con el resumen de la corrida
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import numpy as np


@dataclass
class Run:
    params: dict[str, float | str] = field(default_factory=dict)
    summary: dict[str, float] = field(default_factory=dict)
    radius: np.ndarray = field(default_factory=lambda: np.zeros(0))
    mass: np.ndarray = field(default_factory=lambda: np.zeros(0))
    exits: np.ndarray = field(default_factory=lambda: np.zeros((0, 2)))  # columnas: t, id
    modes: np.ndarray = field(default_factory=lambda: np.zeros((0, 3)))  # columnas: t, id, modo
    frame_count: int = 0

    @property
    def agents(self) -> int:
        return len(self.radius)

    @property
    def scheme(self) -> str:
        return str(self.params.get("scheme", "?"))

    @property
    def finished(self) -> bool:
        return int(self.summary.get("remaining", 1)) == 0


def _number(text: str) -> float | str:
    try:
        return float(text)
    except ValueError:
        return text


def _pairs(tokens: list[str]) -> dict[str, float | str]:
    return {tokens[k]: _number(tokens[k + 1]) for k in range(0, len(tokens) - 1, 2)}


def read_run(path: str | Path, frames: bool = False) -> Run:
    """Lee cabecera, agentes, salidas, cambios de modo y pie. Los cuadros solo se cuentan
    (para leerlos, `iter_frames`)."""
    run = Run()
    radius, mass, exits, modes = [], [], [], []
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                tokens = line[1:].split()
                if tokens and tokens[0] in ("end_time", "isolated_unrelaxed_steps", "exited"):
                    run.summary.update({k: float(v) for k, v in _pairs(tokens).items()})
                elif len(tokens) >= 2 and len(tokens) % 2 == 0 and tokens[0] != "tp5":
                    run.params.update(_pairs(tokens))
            elif line.startswith("agent "):
                _, _, r, m = line.split()
                radius.append(float(r))
                mass.append(float(m))
            elif line.startswith("exit "):
                _, t, i = line.split()
                exits.append((float(t), int(i)))
            elif line.startswith("mode "):
                _, t, i, m = line.split()
                modes.append((float(t), int(i), int(m)))
            elif line.startswith("frame "):
                run.frame_count += 1
    run.radius = np.array(radius)
    run.mass = np.array(mass)
    run.exits = np.array(exits, dtype=float).reshape(-1, 2)
    run.modes = np.array(modes, dtype=float).reshape(-1, 3)
    return run


@dataclass
class Frame:
    time: float
    ids: np.ndarray
    position: np.ndarray  # (n, 2)
    velocity: np.ndarray  # (n, 2)
    mode: np.ndarray      # (n,)


def iter_frames(path: str | Path, every: int = 1) -> Iterator[Frame]:
    """Recorre los cuadros sin cargar todo el archivo; `every` saltea cuadros."""
    index = -1
    time, rows = None, []

    def build() -> Frame:
        data = np.array(rows, dtype=float).reshape(-1, 6)
        return Frame(time, data[:, 0].astype(int), data[:, 1:3], data[:, 3:5], data[:, 5].astype(int))

    with open(path) as fh:
        for line in fh:
            if line.startswith("frame "):
                if time is not None and index % every == 0:
                    yield build()
                index += 1
                time, rows = float(line.split()[1]), []
            elif time is not None and line[:1].isdigit():
                if index % every == 0:
                    rows.append(line.split())
            elif time is not None and not line.startswith(("exit", "mode")):
                if index % every == 0:
                    yield build()
                time, rows = None, []
        if time is not None and index % every == 0:
            yield build()
