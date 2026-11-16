"""Resume la prueba de rigidez y fricción de los contactos (run_exploracion.py): TSDMD puro
con N = AGENTS en las semillas de a y b, con el k y el kappa del paper (experiments/raw/poblacion),
con k diez veces mayor y con k y kappa diez veces mayores. Por variante: fracción de trabadas con
su intervalo de Clopper-Pearson del 95 %, t_evac de las que terminan y, semilla por semilla,
t_evac contra el del paper en las que terminan las dos. Escribe experiments/results/rigidez.csv.

Uso: python scripts/resumen_rigidez.py
"""
from __future__ import annotations

import csv

from common import RAW, RESULTS
from tp5analysis.io import read_run
from tp5analysis.observables import evacuation_time
from tp5analysis.stats import clopper_pearson, mean_std

SEEDS = range(401, 451)
# nombre: (archivo de cada semilla, k, kappa)
VARIANTS = {
    "paper": ("poblacion/tsdmd_seed{}.txt", 1.2e5, 2.4e5),
    "k10": ("exploracion/kn1.2e6_seed{}.txt", 1.2e6, 2.4e5),
    "k10_kappa10": ("exploracion/kn1.2e6_kt2.4e6_seed{}.txt", 1.2e6, 2.4e6),
}


def main() -> None:
    runs = {name: {s: read_run(RAW / pattern.format(s)) for s in SEEDS} for name, (pattern, _, _) in VARIANTS.items()}
    rows = []
    for name, (_, kn, kt) in VARIANTS.items():
        group = runs[name]
        done = {s: r for s, r in group.items() if r.finished}
        clogged = len(group) - len(done)
        low, high = clopper_pearson(clogged, len(group))
        t = mean_std(evacuation_time(r) for r in done.values())
        pairs = [s for s in done if runs["paper"][s].finished]
        d = mean_std(evacuation_time(done[s]) - evacuation_time(runs["paper"][s]) for s in pairs)
        rows.append({"variant": name, "kn": kn, "kt": kt, "runs": len(group), "clogged": clogged,
                     "p_clog": clogged / len(group), "p_low": low, "p_high": high,
                     "t_evac_mean": t[0], "t_evac_std": t[1], "finished": t[2],
                     "pairs": len(pairs), "dt_evac_mean": d[0], "dt_evac_std": d[1]})
        print(f"{name:12s} k = {kn:.1e}, kappa = {kt:.1e}: trabadas {clogged}/{len(group)} (IC 95 %: {low:.0%}–{high:.0%}); "
              f"t_evac = {t[0]:.1f} ± {t[1]:.1f} s ({t[2]}); contra el paper {d[0]:+.1f} ± {d[1]:.1f} s ({len(pairs)} pares)")
    with open(RESULTS / "rigidez.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
