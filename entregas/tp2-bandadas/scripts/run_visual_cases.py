#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path


def tag(value: float) -> str:
    return f"{value:g}".replace(".", "p")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera corridas y GIF característicos con va y S sincronizados."
    )
    parser.add_argument("config", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    config = json.loads(arguments.config.read_text(encoding="utf-8"))
    root = arguments.config.resolve().parents[2]
    binary = root / config.get("binary", "cpp/build/release/tp2")
    if not binary.is_file():
        raise ValueError(f"no existe el motor compilado: {binary}")
    output_dir = root / config.get("output_dir", "experiments/raw/visual-cases")
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / "manifest.json"
    normalized = json.dumps(config, indent=2, sort_keys=True) + "\n"
    if manifest.exists() and manifest.read_text(encoding="utf-8") != normalized:
        raise ValueError(f"{output_dir} ya contiene otra configuración")
    manifest.write_text(normalized, encoding="utf-8")
    cases = config.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases debe ser una lista no vacía")
    defaults = config.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("defaults debe ser un objeto")

    def setting(case: dict, name: str, fallback):
        return case.get(name, defaults.get(name, fallback))

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "python/src")
    for index, case in enumerate(cases, start=1):
        model = str(case["model"])
        density = float(case["density"])
        eta = float(case["eta"])
        seed = int(case["seed"])
        steps = int(setting(case, "steps", 400))
        every = int(setting(case, "trajectory_every", 2))
        fps = float(setting(case, "fps", 5.0))
        side = float(setting(case, "L", 10.0))
        cells = int(setting(case, "M", 9))
        cutoff = float(setting(case, "rc", 1.0))
        speed = float(setting(case, "v", 0.03))
        time_step = float(setting(case, "dt", 1.0))
        if (
            model not in {"vicsek", "voter"}
            or not 0 <= eta <= 1
            or density <= 0
            or seed < 0
            or steps < 1
            or every < 1
            or not math.isfinite(fps)
            or fps <= 0
        ):
            raise ValueError(f"caso {index}: parámetros inválidos")
        stem = f"{model}-rho{tag(density)}-eta{tag(eta)}-seed{seed}"
        observations = output_dir / f"{stem}-observables.csv"
        trajectory = output_dir / f"{stem}-trajectory.csv"
        animation = output_dir / f"{stem}.gif"
        if animation.exists() and not arguments.force:
            if not observations.is_file() or not trajectory.is_file():
                raise ValueError(
                    f"{animation} no tiene sus dos CSV de origen; use --force"
                )
            print(f"[{index}/{len(cases)}] reutilizada {animation.name}")
            continue

        command = [
            str(binary), "simulate",
            "--model", model,
            "--rho", str(density),
            "--eta", str(eta),
            "--steps", str(steps),
            "--seed", str(seed),
            "--M", str(cells),
            "--L", str(side),
            "--rc", str(cutoff),
            "--v", str(speed),
            "--dt", str(time_step),
            "--trajectory-every", str(every),
            "--trajectory", str(trajectory),
            "--observables", str(observations),
        ]
        subprocess.run(command, check=True)
        subprocess.run(
            [
                sys.executable, "-m", "tp2analysis", "animate",
                "--input", str(trajectory),
                "--observables", str(observations),
                "--output", str(animation),
                "--fps", str(fps),
            ],
            check=True,
            env=environment,
        )
        simulated_units_per_second = every * time_step * fps
        print(
            f"[{index}/{len(cases)}] {animation.name}: "
            f"{simulated_units_per_second:g} unidades simuladas/s"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
