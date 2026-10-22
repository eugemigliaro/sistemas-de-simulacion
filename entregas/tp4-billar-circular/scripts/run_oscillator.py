#!/usr/bin/env python3
"""Sistema 1: ECM de los cuatro integradores en función del paso [TP04, p. 1]."""
import subprocess

from common import ENGINE, RAW, RESULTS, parallel, require_engine, write_csv
from tp4analysis import files, oscillator

INTEGRATORS = ["beeman", "verlet", "velocity-verlet", "euler-pc"]
STEPS = [5e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5]


def run(case: tuple[str, float]) -> dict:
    integrator, dt = case
    output = RAW / "oscillator" / f"{integrator}-{dt:g}.txt"
    if not output.exists():
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_suffix(".partial")
        subprocess.run([str(ENGINE), "oscillator", "--integrator", integrator, "--dt", repr(dt),
                        "--output", str(partial)], check=True)
        partial.rename(output)
    header, times, positions = files.read_oscillator(output)
    return {"integrator": integrator, "dt_s": dt, "ecm_m2": oscillator.mean_squared_error(header, times, positions)}


def main() -> None:
    require_engine()
    rows = parallel(run, [(integrator, dt) for integrator in INTEGRATORS for dt in STEPS])
    write_csv(RESULTS / "oscillator-ecm.csv", rows)
    for row in rows:
        print(f"{row['integrator']:16s} dt={row['dt_s']:.0e}  ECM={row['ecm_m2']:.3e} m²")


if __name__ == "__main__":
    main()
