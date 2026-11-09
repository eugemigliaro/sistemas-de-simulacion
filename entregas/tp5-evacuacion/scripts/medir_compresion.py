"""Compresión media de los contactos en el tapón de TSDMD (decisión 7 del 2026-11-09): en la
corrida con cuadros de la semilla 401 (experiments/raw/animaciones/tsdmd_seed401.txt), un
cuadro por segundo, los contactos (xi > 0) entre agentes a menos de 1,5 m del centro de la
puerta. xi_medio es el promedio de todos esos contactos; es la reducción del núcleo duro de
la regla alternativa de EDMD. Escribe experiments/results/compresion.csv.

Uso: python scripts/medir_compresion.py
"""
from __future__ import annotations

import csv

import numpy as np

from common import RAW, RESULTS
from tp5analysis.io import iter_frames, read_run

NEAR = 1.5   # m, radio alrededor del centro de la puerta
EVERY = 10   # cuadros (uno por segundo con output_dt = 0,1 s)


def main() -> None:
    path = RAW / "animaciones" / "tsdmd_seed401.txt"
    run = read_run(path)
    door = np.array([0.5 * float(run.params["side"]), 0.0])
    contacts = []
    for frame in iter_frames(path, every=EVERY):
        near = np.linalg.norm(frame.position - door, axis=1) < NEAR
        x, r = frame.position[near], run.radius[frame.ids[near]]
        xi = r[:, None] + r[None, :] - np.linalg.norm(x[:, None] - x[None, :], axis=2)
        xi = xi[np.triu_indices(len(r), 1)]
        contacts.extend(xi[xi > 0])
    xi = np.array(contacts)
    row = {"agents": run.agents, "contacts": len(xi), "xi_mean": xi.mean(), "xi_median": float(np.median(xi)),
           "xi_max": xi.max()}
    print(f"N = {run.agents}: {len(xi)} contactos; xi medio = {100 * xi.mean():.2f} cm, "
          f"mediana = {100 * np.median(xi):.2f} cm, máximo = {100 * xi.max():.2f} cm")
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / "compresion.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    main()
