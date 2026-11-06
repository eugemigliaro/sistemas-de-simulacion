"""Estudio exploratorio de atascos permanentes (para la consulta con la cátedra).

TSDMD puro con N = 500: 20 semillas sin fluctuación y 10 por amplitud de fluctuación en
contacto (las mismas semillas que las primeras 10 sin fluctuación: comparación pareada).
Corte por atasco: 300 s sin salidas. Se saltean las salidas ya escritas.

Uso: python scripts/run_atascos.py [trabajos en paralelo]
"""
from __future__ import annotations

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "cpp" / "build" / "release" / "tp5"
OUT = ROOT / "experiments" / "raw" / "atascos"

RUNS = [(0.0, seed) for seed in range(101, 121)]
RUNS += [(noise, seed) for noise in (0.05, 0.1, 0.2) for seed in range(101, 111)]


def run(noise: float, seed: int) -> str:
    path = OUT / f"noise{noise:g}_seed{seed}.txt"
    if path.exists() and "# exited" in path.read_text()[-400:]:
        return f"{path.name}: ya estaba"
    command = [str(ENGINE), "evacuate", "--scheme", "tsdmd", "--seed", str(seed), "--noise", f"{noise:g}",
               "--clog-time", "300", "--t-max", "4000", "--output", str(path)]
    result = subprocess.run(command, capture_output=True, text=True)
    return f"{path.name}: {result.stderr.strip()}"


def main() -> None:
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for line in pool.map(lambda r: run(*r), RUNS):
            print(line, flush=True)


if __name__ == "__main__":
    main()
