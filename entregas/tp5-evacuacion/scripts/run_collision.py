"""Choque aislado de dos agentes (`tp5 collision`): valida la regla de choque del EDMD contra
el contacto blando del SFM y el dt del TSDMD. Escribe experiments/results/collision-rule.csv
(barrido de rapidez y parámetro de impacto con dt = 0,1 ms) y collision-dt.csv (choque
frontal de los dos agentes más livianos con varios dt).

Uso: python scripts/run_collision.py
"""
from __future__ import annotations

import csv
import subprocess

from common import ENGINE, RESULTS


def collide(**options) -> dict[str, float]:
    command = [str(ENGINE), "collision"] + [x for k, v in options.items() for x in (f"--{k.replace('_', '-')}", f"{v:g}")]
    out = subprocess.run(command, capture_output=True, text=True, check=True).stdout.split()
    return {out[k]: float(out[k + 1]) for k in range(0, len(out) - 1, 2) if out[k + 1][:1] in "-0123456789."}


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for offset in (0.2, 0.5, 0.8):
        for speed in (0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0):
            r = collide(dt=1e-4, speed=speed, offset=offset)
            rows.append({"offset": offset, "speed": speed, **{k: r[k] for k in (
                "contact_time", "max_overlap", "normal_ratio", "tangential_ratio", "hard_normal_ratio",
                "hard_tangential_ratio")}})
    with open(RESULTS / "collision-rule.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    rows = []
    for dt in (5e-3, 3e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5):
        r = collide(dt=dt, radius_i=0.18, radius_j=0.18, speed=1.5)
        rows.append({"dt": dt, "contact_time": r["contact_time"], "max_overlap": r["max_overlap"],
                     "normal_ratio": r["normal_ratio"]})
    with open(RESULTS / "collision-dt.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("choques aislados: collision-rule.csv y collision-dt.csv")


if __name__ == "__main__":
    main()
