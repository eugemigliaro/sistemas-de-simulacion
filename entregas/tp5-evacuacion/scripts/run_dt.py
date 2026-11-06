"""Test estadístico del paso temporal: TSDMD puro, N = 500, dt en {2; 1; 0,5} ms con las
mismas 10 semillas (201 a 210). El choque aislado está en `tp5 collision` (run_collision.py).

Uso: python scripts/run_dt.py
"""
from common import RAW, evacuate, run_all

DTS = (2e-3, 1e-3, 5e-4)
SEEDS = range(201, 211)


def main() -> None:
    jobs = []
    for dt in DTS:
        for seed in SEEDS:
            path = RAW / "dt" / f"dt{dt:g}_seed{seed}.txt"
            jobs.append((path, evacuate(path, scheme="tsdmd", dt=dt, seed=seed)))
    run_all(jobs)


if __name__ == "__main__":
    main()
