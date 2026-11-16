"""Resume el estudio para elegir N (run_elegir_n.py): por N, costo por segundo simulado de
cada esquema y, semilla por semilla, el del híbrido sobre el de TSDMD y sobre el de EDMD
puro, con corridas trabadas. Aplica el criterio acordado: califican los N donde las dos
relaciones están por debajo de 1 por más de 3 errores estándar; se elige el de mayor margen
sobre el segundo mejor, 1 - máx(relaciones). Escribe experiments/results/elegir-n.csv.

Uso: python scripts/resumen_elegir_n.py
"""
from __future__ import annotations

import csv
import math
import re

from common import RAW, RESULTS
from tp5analysis.io import read_run
from tp5analysis.observables import evacuation_time
from tp5analysis.stats import mean_std

SCHEMES = ("tsdmd", "hybrid", "edmd")


def main() -> None:
    runs: dict[tuple[int, str], dict[int, object]] = {}
    for path in sorted((RAW / "elegir_n").glob("n*_seed*.txt")):
        n, scheme, seed = re.match(r"n(\d+)_(\w+)_seed(\d+)", path.stem).groups()
        run = read_run(path)
        if "exited" in run.summary:
            runs.setdefault((int(n), scheme), {})[int(seed)] = run

    def cost(run) -> float:
        return float(run.summary["wall_seconds"]) / float(run.summary["end_time"])

    rows = []
    for n in sorted({n for n, _ in runs}):
        group = {s: runs.get((n, s), {}) for s in SCHEMES}
        seeds = sorted(set.intersection(*(set(g) for g in group.values())))
        row = {"agents": n, "pairs": len(seeds)}
        for s in SCHEMES:
            c = mean_std(cost(group[s][k]) for k in seeds)
            row[f"{s}_cost_mean"], row[f"{s}_cost_std"] = c[0], c[1]
            row[f"{s}_clogged"] = sum(1 for k in seeds if not group[s][k].finished)
            t = mean_std(evacuation_time(group[s][k]) for k in seeds)
            row[f"{s}_t_evac_mean"], row[f"{s}_t_evac_std"] = t[0], t[1]
        for other in ("tsdmd", "edmd"):
            r = mean_std(cost(group["hybrid"][k]) / cost(group[other][k]) for k in seeds)
            row[f"hybrid_over_{other}_mean"], row[f"hybrid_over_{other}_std"] = r[0], r[1]
            row[f"hybrid_over_{other}_se"] = r[1] / math.sqrt(r[2]) if r[2] else float("nan")
        best = all(row[f"hybrid_over_{o}_mean"] + 3 * row[f"hybrid_over_{o}_se"] < 1 for o in ("tsdmd", "edmd"))
        row["hybrid_best"] = int(best)
        row["margin"] = 1 - max(row["hybrid_over_tsdmd_mean"], row["hybrid_over_edmd_mean"])
        rows.append(row)
        print(f"N = {n:3d}: costo (ms/s) TSDMD {1e3 * row['tsdmd_cost_mean']:6.2f}, híbrido {1e3 * row['hybrid_cost_mean']:6.2f}, "
              f"EDMD {1e3 * row['edmd_cost_mean']:6.2f}; híbrido/TSDMD {row['hybrid_over_tsdmd_mean']:.3f} "
              f"(ee {row['hybrid_over_tsdmd_se']:.3f}), híbrido/EDMD {row['hybrid_over_edmd_mean']:.3f} "
              f"(ee {row['hybrid_over_edmd_se']:.3f}); trabadas T/H/E {row['tsdmd_clogged']}/{row['hybrid_clogged']}/"
              f"{row['edmd_clogged']} de {len(seeds)}; {'califica' if best else 'no califica'}, margen {row['margin']:+.3f}")
    eligible = [r for r in rows if r["hybrid_best"]]
    if eligible:
        chosen = max(eligible, key=lambda r: r["margin"])
        print(f"N elegido: {chosen['agents']} (margen {chosen['margin']:.1%} sobre el segundo mejor)")
    else:
        print("ningún N cumple el criterio")
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / "elegir-n.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
