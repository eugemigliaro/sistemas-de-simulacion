#!/usr/bin/env python3
"""Determina un N alto reproducible para los experimentos del TP1."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def can_generate(
    binary: Path,
    particle_count: int,
    boundary: str,
    seeds: list[int],
    attempts: int,
) -> tuple[bool, int | None, str | None]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for seed in seeds:
            command = [
                str(binary),
                "generate",
                "--N",
                str(particle_count),
                "--L",
                "20",
                "--r-min",
                "0.23",
                "--r-max",
                "0.26",
                "--seed",
                str(seed),
                "--boundary",
                boundary,
                "--attempts",
                str(attempts),
                "--static",
                str(root / "static.txt"),
                "--dynamic",
                str(root / "dynamic.txt"),
            ]
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return False, seed, result.stderr.strip()
    return True, None, None


def calibrate_boundary(
    binary: Path,
    boundary: str,
    seeds: list[int],
    attempts: int,
    step: int,
) -> tuple[int, list[dict[str, object]]]:
    observations: list[dict[str, object]] = []

    def test(units: int) -> bool:
        particle_count = units * step
        print(f"Probando boundary={boundary}, N={particle_count}", flush=True)
        success, failed_seed, error = can_generate(
            binary, particle_count, boundary, seeds, attempts
        )
        observations.append(
            {
                "N": particle_count,
                "success": success,
                "failed_seed": failed_seed,
                "error": error,
            }
        )
        return success

    lower_units = 0
    upper_units = 2
    while test(upper_units):
        lower_units = upper_units
        upper_units *= 2

    while upper_units - lower_units > 1:
        middle_units = (lower_units + upper_units) // 2
        if test(middle_units):
            lower_units = middle_units
        else:
            upper_units = middle_units

    return lower_units * step, observations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Busca el mayor N reproducible para paredes y periodicidad."
    )
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", required=True)
    parser.add_argument("--attempts", type=int, default=100_000)
    parser.add_argument("--step", type=int, default=50)
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    if not arguments.binary.is_file():
        raise SystemExit(f"no existe el ejecutable {arguments.binary}")
    if arguments.attempts <= 0 or arguments.step <= 0:
        raise SystemExit("attempts y step deben ser positivos")
    if not arguments.seeds or any(seed < 0 for seed in arguments.seeds):
        raise SystemExit("seeds debe contener enteros no negativos")

    maximum_by_boundary: dict[str, int] = {}
    observations: dict[str, list[dict[str, object]]] = {}
    for boundary in ("walls", "periodic"):
        maximum, boundary_observations = calibrate_boundary(
            arguments.binary.resolve(),
            boundary,
            arguments.seeds,
            arguments.attempts,
            arguments.step,
        )
        maximum_by_boundary[boundary] = maximum
        observations[boundary] = boundary_observations

    maximum = min(maximum_by_boundary.values())
    intermediate = max(arguments.step, (maximum // (2 * arguments.step)) * arguments.step)
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "definition": (
            "largest multiple of step generated for every configured seed "
            "with the configured attempt limit"
        ),
        "L": 20.0,
        "rc": 1.0,
        "r_min": 0.23,
        "r_max": 0.26,
        "attempts_per_particle": arguments.attempts,
        "step": arguments.step,
        "seeds": arguments.seeds,
        "maximum_by_boundary": maximum_by_boundary,
        "N_high": maximum,
        "N_intermediate": intermediate,
        "observations": observations,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"N_intermediate={intermediate}, N_high={maximum}; "
        f"resultado escrito en {arguments.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
