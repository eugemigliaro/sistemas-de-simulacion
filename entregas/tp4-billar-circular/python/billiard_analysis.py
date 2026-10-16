"""Lectura por cuadros y energia calculada exclusivamente desde estados guardados."""
import gzip
from pathlib import Path

import numpy as np

HEADER = "step,time,id,x,y,vx,vy,used,first_contact_step"


def frames(path, config):
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    n = config["n"]
    expected_step = 0
    previous_contact = np.full(n, -1.0)
    with opener(path, "rt") as handle:
        if handle.readline().strip() != HEADER:
            raise ValueError("Cabecera de billar invalida")
        while True:
            first_line = handle.readline()
            if not first_line:
                break
            lines = [first_line] + [handle.readline() for _ in range(n - 1)]
            if any(not line for line in lines):
                raise ValueError("Cuadro incompleto")
            values = np.fromstring("".join(lines).replace("\n", ",").rstrip(","), sep=",")
            if values.size != n * 9 or not np.isfinite(values).all():
                raise ValueError("Estado no finito o cuadro mal formado")
            state = values.reshape(n, 9)
            time = expected_step * config["dt"]
            if not np.all(state[:, 0] == expected_step) or not np.allclose(state[:, 1], time, rtol=0, atol=1e-12):
                raise ValueError("Pasos o tiempos inconsistentes")
            if not np.array_equal(state[:, 2], np.arange(n)):
                raise ValueError("IDs inconsistentes")
            contact = state[:, 8]
            if (not np.all(contact == np.floor(contact)) or np.any(contact < -1) or
                    np.any(contact > expected_step) or not np.array_equal(state[:, 7], contact >= 0)):
                raise ValueError("Estado fresca/usada inconsistente")
            if np.any(contact[previous_contact >= 0] != previous_contact[previous_contact >= 0]):
                raise ValueError("Conversion reversible o repetida")
            if expected_step == 0 and np.any(contact != -1):
                raise ValueError("Estado inicial usado")
            previous_contact = contact.copy()
            yield expected_step, time, state
            expected_step += config["save_every"]
    if expected_step != config["steps"] + config["save_every"]:
        raise ValueError("Trayectoria incompleta o horizonte incompatible")


class Energy:
    def __init__(self, config):
        self.c = config
        self.i, self.j = np.triu_indices(config["n"], 1)

    def components(self, state):
        c = self.c
        positions, velocities = state[:, 3:5], state[:, 5:7]
        kinetic = c["mass"] * np.sum(velocities * velocities) / 2
        delta = positions[self.i] - positions[self.j]
        overlaps = np.maximum(0, 2 * c["particle_radius"] - np.sqrt(np.sum(delta * delta, axis=1)))
        pair = c["stiffness"] * np.sum(overlaps**2) / 2
        wall_overlap = np.maximum(0, np.sqrt(np.sum(positions**2, axis=1)) + c["particle_radius"] - c["radius"])
        wall = c["stiffness"] * np.sum(wall_overlap**2) / 2
        obstacle = 0.0
        if c["obstacles"]:
            for x in [-c["obstacle_x"], c["obstacle_x"]]:
                distance = np.sqrt(np.sum((positions - [x, 0])**2, axis=1))
                overlap = np.maximum(0, 2 * c["particle_radius"] - distance)
                obstacle += c["stiffness"] * np.sum(overlap**2) / 2
        return float(kinetic), float(pair), float(wall), float(obstacle)


def energy_series(path, config):
    calculator = Energy(config)
    records = []
    for step, time, state in frames(path, config):
        components = calculator.components(state)
        records.append((step, time, *components, sum(components)))
    series = np.asarray(records)
    if not np.isfinite(series).all() or series[0, -1] <= 0:
        raise ValueError("Energia no finita o inicial no positiva")
    return series


def maximum_relative_error(series):
    return float(np.max(np.abs(series[:, -1] / series[0, -1] - 1)))
