"""Resume el estudio de atascos: por amplitud de fluctuación, fracción de corridas trabadas
con su intervalo de Clopper-Pearson del 95 %, t_evac de las que terminan y agentes que
quedan en las trabadas. Escribe experiments/results/atascos.csv.

Uso: python scripts/resumen_atascos.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python" / "src"))

from tp5analysis.io import read_run  # noqa: E402
from tp5analysis.observables import evacuation_time, last_exit  # noqa: E402
from tp5analysis.stats import clopper_pearson, mean_std  # noqa: E402

RAW = ROOT / "experiments" / "raw" / "atascos"
OUT = ROOT / "experiments" / "results" / "atascos.csv"


def main() -> None:
    groups: dict[float, list] = {}
    for path in sorted(RAW.glob("noise*_seed*.txt")):
        run = read_run(path)
        if "exited" not in run.summary:
            continue  # todavía corriendo
        noise = float(run.params["noise"])
        groups.setdefault(noise, []).append(run)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for noise, runs in sorted(groups.items()):
        clogged = [r for r in runs if r.summary.get("clogged", 0) == 1 or r.summary.get("remaining", 0) > 0]
        finished = [r for r in runs if r not in clogged]
        low, high = clopper_pearson(len(clogged), len(runs))
        t_mean, t_std, t_n = mean_std(evacuation_time(r) for r in finished)
        left = [int(r.summary["remaining"]) for r in clogged]
        last = [last_exit(r) for r in clogged]
        rows.append({
            "noise": noise, "runs": len(runs), "clogged": len(clogged),
            "p_clog": len(clogged) / len(runs), "p_low": low, "p_high": high,
            "t_evac_mean": t_mean, "t_evac_std": t_std, "finished": t_n,
            "left_min": min(left) if left else "", "left_max": max(left) if left else "",
            "last_exit_min": min(last) if last else "", "last_exit_max": max(last) if last else "",
        })
        print(f"fluctuación {noise:4.0%}: trabadas {len(clogged)}/{len(runs)} "
              f"(IC 95 %: {low:.0%}–{high:.0%}); t_evac = {t_mean:.0f} ± {t_std:.0f} s en {t_n} que terminaron"
              + (f"; en las trabadas quedan {min(left)}–{max(left)} adentro" if left else ""))
    with open(OUT, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["noise"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
