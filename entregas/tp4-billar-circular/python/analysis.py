"""Referencia analitica y observables; no participa en el motor C++."""
from pathlib import Path

import numpy as np


def exact_position(time, config):
    """Solucion para cualquier amortiguamiento y condicion inicial del CLI."""
    t = np.asarray(time, dtype=float)
    beta = config["damping"] / (2 * config["mass"])
    omega2 = config["stiffness"] / config["mass"]
    delta = omega2 - beta**2
    x0, v0 = config["x0"], config["v0"]
    if delta > 0:
        omega = np.sqrt(delta)
        return np.exp(-beta * t) * (
            x0 * np.cos(omega * t) + (v0 + beta * x0) * np.sin(omega * t) / omega
        )
    if delta == 0:
        return np.exp(-beta * t) * (x0 + (v0 + beta * x0) * t)
    root = np.sqrt(-delta)
    # Evita el producto exp(-beta*t)*cosh(root*t), que puede desbordar.
    r1, r2 = -omega2 / (beta + root), -beta - root
    c1 = (v0 - r2 * x0) / (r1 - r2)
    return c1 * np.exp(r1 * t) + (x0 - c1) * np.exp(r2 * t)


def load_trajectory(path: Path, config, steps):
    data = np.genfromtxt(path, delimiter=",", names=True, ndmin=1)
    if data.dtype.names != ("step", "time", "position", "velocity"):
        raise ValueError(f"Columnas inesperadas: {path}")
    if len(data) != steps + 1:
        raise ValueError(f"Cantidad de muestras incorrecta: {path}")
    if not all(np.isfinite(data[name]).all() for name in data.dtype.names):
        raise ValueError(f"Estado no finito: {path}")
    if not np.array_equal(data["step"], np.arange(steps + 1)):
        raise ValueError(f"Indices incorrectos: {path}")
    expected_time = np.arange(steps + 1) * (config["duration"] / steps)
    expected_time[-1] = config["duration"]
    tolerance = 16 * np.finfo(float).eps * max(1, config["duration"])
    if not np.allclose(data["time"], expected_time, rtol=0, atol=tolerance):
        raise ValueError(f"Tiempos incompatibles: {path}")
    if data["position"][0] != config["x0"] or data["velocity"][0] != config["v0"]:
        raise ValueError(f"Condicion inicial incorrecta: {path}")
    return data


def position_errors(data, config):
    """Promedio temporal n=1,...,M; excluye la condicion inicial."""
    error = data["position"][1:] - exact_position(data["time"][1:], config)
    if not len(error):
        raise ValueError("No hay pasos para calcular ECM")
    ecm = float(np.mean(error**2))
    max_error = float(np.max(np.abs(error)))
    if not np.isfinite(ecm) or not np.isfinite(max_error):
        raise ValueError("Error no finito")
    return ecm, max_error
