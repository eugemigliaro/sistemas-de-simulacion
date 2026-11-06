"""Elección de T* con un benchmark corto y controlado: corridas de a una, alternando los
valores de T_STARS y el TSDMD puro, con la semilla 501 y los primeros 150 s simulados (todo
el vuelo libre está ahí; después todos son TSDMD y cuestan lo mismo). Tres repeticiones; se
elige el T* con menor tiempo mínimo. Es solo para elegir T*: el punto c oficial es
run_tiempos.py. Escribe experiments/results/bench_tstar.csv.

Uso: python scripts/bench_tstar.py
"""
from __future__ import annotations

import csv
import re
import subprocess
import tempfile
from pathlib import Path

from common import DT, RESULTS, SECOND_TARGET, T_STARS, evacuate

REPETITIONS = 3
HORIZON = 150.0


def main() -> None:
    configs = [("tsdmd", {})] + [(f"hybrid T*={t:g}", {"scheme": "hybrid", "t_star": t}) for t in T_STARS]
    times: dict[str, list[float]] = {name: [] for name, _ in configs}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "bench.txt"
        for rep in range(REPETITIONS):
            for name, extra in configs:
                options = {"scheme": "tsdmd", **extra}
                command = evacuate(out, dt=DT, seed=501, t_max=HORIZON, **SECOND_TARGET, **options)
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                wall = float(re.search(r"wall ([\d.]+) s", result.stderr).group(1))
                times[name].append(wall)
                print(f"repetición {rep + 1}: {name:18s} {wall:.2f} s", flush=True)
    rows = [{"config": name, "min": min(v), "median": sorted(v)[len(v) // 2], "runs": len(v)} for name, v in times.items()]
    for r in rows:
        print(f"{r['config']:18s} mínimo {r['min']:.2f} s  mediana {r['median']:.2f} s")
    best = min((r for r in rows if r["config"].startswith("hybrid")), key=lambda r: r["min"])
    print(f"T* elegido: {best['config']}")
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / "bench_tstar.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
