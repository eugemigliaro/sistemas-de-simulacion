"""Lectura de las salidas de texto del motor (formato en cpp/include/tp4/io.hpp)."""
from __future__ import annotations

import gzip
from dataclasses import dataclass
from pathlib import Path

import numpy as np

INTEGER_KEYS = {"particles", "seed", "steps", "output_every"}
TEXT_KEYS = {"tp4", "layout", "integrator", "obstacle_x", "columns"}


def _open(path: Path):
    return gzip.open(path, "rt") if path.suffix == ".gz" else open(path)


def read_header(path: str | Path) -> dict:
    header = {}
    with _open(Path(path)) as stream:
        for line in stream:
            if not line.startswith("#"):
                break
            key, _, value = line[1:].strip().partition(" ")
            if not value:
                continue
            if key in INTEGER_KEYS:
                header[key] = int(value)
            elif key in TEXT_KEYS:
                header[key] = value
            else:
                header[key] = float(value)
    if header.get("obstacle_x") not in (None, "none"):
        header["obstacle_x"] = float(header["obstacle_x"])
    elif "obstacle_x" in header:
        header["obstacle_x"] = None
    return header


@dataclass
class Trajectory:
    header: dict
    times: np.ndarray  # (cuadros,)
    states: np.ndarray  # (cuadros, N, 5): x, y, vx, vy, color

    @property
    def positions(self) -> np.ndarray:
        return self.states[:, :, 0:2]

    @property
    def velocities(self) -> np.ndarray:
        return self.states[:, :, 2:4]

    @property
    def used(self) -> np.ndarray:
        return self.states[:, :, 4] > 0.5


def read_billiard(path: str | Path, truncated: bool = False) -> Trajectory:
    """Con truncated=True acepta una corrida detenida antes de tf (por ejemplo,
    porque el paso era demasiado grande) y devuelve los cuadros completos."""
    path = Path(path)
    header = read_header(path)
    n = header["particles"]
    frames = header["steps"] // header["output_every"] + 1
    data = np.loadtxt(path, comments=("#", "frame"), ndmin=2)
    if truncated:
        frames = min(frames, len(data) // n)
        data = data[:frames * n]
    if data.shape != (frames * n, 5) or frames == 0:
        raise ValueError(f"{path}: se esperaban {frames} cuadros de {n} partículas")
    times = np.arange(frames) * header["output_every"] * header["dt"]
    return Trajectory(header, times, data.reshape(frames, n, 5))


def read_oscillator(path: str | Path) -> tuple[dict, np.ndarray, np.ndarray]:
    """Devuelve la cabecera, los tiempos y las posiciones."""
    path = Path(path)
    data = np.loadtxt(path, comments="#", ndmin=2)
    if data.shape[1] != 4 or not np.array_equal(data[:, 0], np.arange(len(data))):
        raise ValueError(f"{path}: muestras del oscilador incompletas")
    return read_header(path), data[:, 1], data[:, 2]
