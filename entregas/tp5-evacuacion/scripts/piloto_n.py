"""Prueba para elegir N (decisión 1 del 2026-11-14): con N = 50 y L = 50 m, 10 semillas
(801 a 810), el híbrido (T* = T_STAR) contra el TSDMD de la misma semilla. Corridas de a una,
alternando el orden. Medida: costo por segundo simulado del híbrido sobre el de TSDMD. Si el
ahorro medio es de al menos 20 % y está a más de 3 errores estándar de 0, N = 50; si no, N = 20.
Escribe experiments/results/piloto-n<N>.csv.

Uso: python scripts/piloto_n.py [N]
"""
from __future__ import annotations

import csv
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from common import DT, RESULTS, SECOND_TARGET, T_STAR, evacuate

SEEDS = range(801, 811)


def run(out: Path, **options) -> tuple[float, float, bool]:
    result = subprocess.run(evacuate(out, dt=DT, **SECOND_TARGET, **options), capture_output=True, text=True,
                            check=True)
    line = result.stderr.strip().splitlines()[-1]
    end = float(re.search(r" t=([\d.]+) s", line).group(1))
    wall = float(re.search(r"wall ([\d.]+) s", line).group(1))
    return wall, end, "(atasco)" not in line


def main() -> None:
    agents = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "piloto.txt"
        for k, seed in enumerate(SEEDS):
            order = ("tsdmd", "hybrid") if k % 2 == 0 else ("hybrid", "tsdmd")
            got = {}
            for scheme in order:
                extra = {"t_star": T_STAR} if scheme == "hybrid" else {}
                got[scheme] = run(out, scheme=scheme, agents=agents, seed=seed, **extra)
            cost = {s: w / e for s, (w, e, _) in got.items()}
            rows.append({"agents": agents, "seed": seed, "tsdmd_wall": got["tsdmd"][0], "tsdmd_end": got["tsdmd"][1],
                         "tsdmd_finished": int(got["tsdmd"][2]), "hybrid_wall": got["hybrid"][0],
                         "hybrid_end": got["hybrid"][1], "hybrid_finished": int(got["hybrid"][2]),
                         "cost_ratio": cost["hybrid"] / cost["tsdmd"]})
            print(f"semilla {seed}: TSDMD {got['tsdmd'][0]:.3f} s ({got['tsdmd'][1]:.0f} s simulados), "
                  f"híbrido {got['hybrid'][0]:.3f} s ({got['hybrid'][1]:.0f} s); relación {rows[-1]['cost_ratio']:.3f}",
                  flush=True)
    ratios = [r["cost_ratio"] for r in rows]
    mean = sum(ratios) / len(ratios)
    std = math.sqrt(sum((x - mean) ** 2 for x in ratios) / (len(ratios) - 1))
    se = std / math.sqrt(len(ratios))
    saving = 1 - mean
    ok = saving >= 0.20 and saving > 3 * se
    print(f"N = {agents}: costo híbrido / TSDMD = {mean:.3f} ± {std:.3f} (error estándar {se:.3f}); "
          f"ahorro {saving:.1%} -> {'se cumple' if ok else 'no se cumple'} el criterio (≥ 20 % y > 3 errores estándar)")
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / f"piloto-n{agents}.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
