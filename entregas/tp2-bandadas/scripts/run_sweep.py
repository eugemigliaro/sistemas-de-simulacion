#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def tag(value: float) -> str:
    return f"{value:g}".replace("-", "m").replace(".", "p")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta un barrido reproducible del motor del TP2."
    )
    parser.add_argument("config", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def require_list(config: dict, key: str) -> list:
    value = config.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} debe ser una lista no vacía")
    return value


def main() -> int:
    arguments = parse_args()
    config = json.loads(arguments.config.read_text(encoding="utf-8"))
    root = arguments.config.resolve().parents[2]
    binary = root / config.get("binary", "cpp/build/release/tp2")
    output_dir = root / config.get("output_dir", "experiments/raw/pilot")
    output_dir.mkdir(parents=True, exist_ok=True)

    models = require_list(config, "models")
    densities = require_list(config, "densities")
    etas = require_list(config, "etas")
    seeds = require_list(config, "seeds")
    steps = int(config["steps"])
    cells = int(config.get("M", 9))
    if steps < 0 or cells <= 0:
        raise ValueError("steps y M fuera de rango")

    total = len(models) * len(densities) * len(etas) * len(seeds)
    completed = 0
    skipped = 0
    for model in models:
        if model not in {"vicsek", "voter"}:
            raise ValueError(f"modelo desconocido: {model}")
        for density in densities:
            for eta in etas:
                for seed in seeds:
                    stem = (
                        f"{model}-rho{tag(float(density))}"
                        f"-eta{tag(float(eta))}-seed{int(seed)}"
                    )
                    observations = output_dir / f"{stem}-observables.csv"
                    if observations.exists() and not arguments.force:
                        skipped += 1
                        continue
                    command = [
                        str(binary),
                        "simulate",
                        "--model",
                        str(model),
                        "--rho",
                        str(density),
                        "--eta",
                        str(eta),
                        "--steps",
                        str(steps),
                        "--seed",
                        str(seed),
                        "--M",
                        str(cells),
                        "--observables",
                        str(observations),
                    ]
                    process = subprocess.run(
                        command,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    if process.returncode != 0:
                        raise RuntimeError(
                            f"falló {stem}: {process.stderr.strip()}"
                        )
                    completed += 1
                    print(f"[{completed + skipped}/{total}] {stem}", flush=True)

    print(
        f"Barrido terminado: {completed} ejecutadas, {skipped} reutilizadas."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
