"""Resume el estudio del segundo target: por opción, corridas trabadas, t_evac de las que
terminan y caudal J. Aplica la regla acordada: la opción con menor t_evac medio, salvo que
su barra (media ± desvío) se superponga con la de "alejarse", en cuyo caso queda
"alejarse". Escribe experiments/results/segundo_target.csv.

Uso: python scripts/resumen_segundo_target.py
"""
from __future__ import annotations

import csv
import re

from common import RAW, RESULTS
from tp5analysis.io import read_run
from tp5analysis.observables import evacuation_time, flow
from tp5analysis.stats import mean_std


def main() -> None:
    groups: dict[str, list] = {}
    for path in sorted((RAW / "segundo_target").glob("*_seed*.txt")):
        option = re.match(r"(.+)_seed\d+", path.stem).group(1)
        run = read_run(path)
        if "exited" in run.summary:
            groups.setdefault(option, []).append(run)

    def distance(option: str) -> float:
        return float("inf") if option == "away" else float(option.removeprefix("point"))

    rows = []
    for option in sorted(groups, key=distance):
        runs = groups[option]
        t_mean, t_std, t_n = mean_std(evacuation_time(r) for r in runs)
        j_mean, j_std, _ = mean_std(flow(r) for r in runs)
        rows.append({"option": option, "distance": distance(option), "runs": len(runs),
                     "clogged": sum(1 for r in runs if not r.finished), "t_evac_mean": t_mean, "t_evac_std": t_std,
                     "finished": t_n, "flow_mean": j_mean, "flow_std": j_std})
        label = "alejarse (-y)" if option == "away" else f"punto a D = {distance(option):g} m"
        print(f"{label:22s} trabadas {rows[-1]['clogged']}/{len(runs)}; t_evac = {t_mean:.0f} ± {t_std:.0f} s "
              f"({t_n} terminan); J = {j_mean:.3f} ± {j_std:.3f} p/s")
    valid = [r for r in rows if r["finished"] >= 2]
    best = min(valid, key=lambda r: r["t_evac_mean"])
    away = next(r for r in rows if r["option"] == "away")
    overlap = abs(best["t_evac_mean"] - away["t_evac_mean"]) <= best["t_evac_std"] + away["t_evac_std"]
    chosen = away if overlap else best
    print(f"menor t_evac: {best['option']}; se superpone con alejarse: {'sí' if overlap else 'no'} -> se usa "
          f"{chosen['option']}")
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / "segundo_target.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) + ["chosen"])
        writer.writeheader()
        for r in rows:
            writer.writerow({**r, "chosen": int(r is chosen)})


if __name__ == "__main__":
    main()
