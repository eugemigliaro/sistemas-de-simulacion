#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
from pathlib import Path


OBSERVATION_FIELDS = (
    "model", "density", "particle_count", "side", "cells_per_side",
    "cutoff", "speed", "time_step", "eta", "seed", "time",
    "polarization", "largest_cluster_fraction", "cim_time_ns",
    "neighbor_pairs", "distance_evaluations",
)


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


def read_systems(config: dict, side: float) -> list[dict]:
    if "systems" not in config:
        result = []
        for value in require_list(config, "densities"):
            density = float(value)
            count = round(density * side * side)
            result.append(
                {
                    "density": density,
                    "particle_count": count,
                    "label": f"rho={density:g}",
                }
            )
        return result

    systems = require_list(config, "systems")
    result = []
    for index, system in enumerate(systems):
        if not isinstance(system, dict):
            raise ValueError(f"systems[{index}] debe ser un objeto")
        density = float(system["density"])
        count = int(system["particle_count"])
        expected = density * side * side
        if density <= 0 or count <= 0 or not math.isclose(expected, count, abs_tol=1e-9):
            raise ValueError(
                f"systems[{index}]: density, particle_count y L son incompatibles"
            )
        result.append(
            {
                "density": density,
                "particle_count": count,
                "label": str(system.get("label", f"rho={density:g}")),
            }
        )
    return result


def model_etas(config: dict, model: str) -> list[float]:
    if "model_etas" in config:
        mapping = config["model_etas"]
        if not isinstance(mapping, dict) or model not in mapping:
            raise ValueError(f"falta model_etas para {model}")
        values = mapping[model]
        if not isinstance(values, list) or not values:
            raise ValueError(f"model_etas[{model}] debe ser una lista no vacía")
    else:
        values = require_list(config, "etas")
    result = [float(value) for value in values]
    if any(not 0 <= value <= 1 for value in result) or len(result) != len(set(result)):
        raise ValueError(f"valores eta inválidos o repetidos para {model}")
    return result


def validate_manifest(output_dir: Path, config: dict) -> None:
    manifest = output_dir / "manifest.json"
    normalized = json.dumps(config, indent=2, sort_keys=True) + "\n"
    if manifest.exists() and manifest.read_text(encoding="utf-8") != normalized:
        raise ValueError(
            f"{output_dir} ya contiene otra configuración; use otro output_dir"
        )
    manifest.write_text(normalized, encoding="utf-8")


def observations_are_complete(
    path: Path,
    *,
    model: str,
    density: float,
    particle_count: int,
    side: float,
    cells: int,
    cutoff: float,
    speed: float,
    time_step: float,
    eta: float,
    seed: int,
    steps: int,
) -> bool:
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != OBSERVATION_FIELDS:
                return False
            count = 0
            for count, row in enumerate(reader, start=1):
                expected_time = (count - 1) * time_step
                if (
                    row["model"] != model
                    or int(row["particle_count"]) != particle_count
                    or int(row["cells_per_side"]) != cells
                    or int(row["seed"]) != seed
                    or not math.isclose(float(row["density"]), density)
                    or not math.isclose(float(row["side"]), side)
                    or not math.isclose(float(row["cutoff"]), cutoff)
                    or not math.isclose(float(row["speed"]), speed)
                    or not math.isclose(float(row["time_step"]), time_step)
                    or not math.isclose(float(row["eta"]), eta)
                    or not math.isclose(float(row["time"]), expected_time)
                ):
                    return False
    except (OSError, KeyError, TypeError, ValueError):
        return False
    return count == steps + 1


def main() -> int:
    arguments = parse_args()
    config = json.loads(arguments.config.read_text(encoding="utf-8"))
    root = arguments.config.resolve().parents[2]
    binary = root / config.get("binary", "cpp/build/release/tp2")
    if not binary.is_file():
        raise ValueError(f"no existe el motor compilado: {binary}")
    output_dir = root / config.get("output_dir", "experiments/raw/pilot")
    output_dir.mkdir(parents=True, exist_ok=True)

    models = [str(value) for value in require_list(config, "models")]
    if any(model not in {"vicsek", "voter"} for model in models):
        raise ValueError("models solo admite vicsek y voter")
    if len(models) != len(set(models)):
        raise ValueError("models contiene valores repetidos")
    seeds = [int(value) for value in require_list(config, "seeds")]
    if any(seed < 0 for seed in seeds) or len(seeds) != len(set(seeds)):
        raise ValueError("seeds contiene valores inválidos o repetidos")

    side = float(config.get("L", 10.0))
    cutoff = float(config.get("rc", 1.0))
    speed = float(config.get("v", 0.03))
    time_step = float(config.get("dt", 1.0))
    steps = int(config["steps"])
    cells = int(config.get("M", 9))
    if (
        side <= 0 or cutoff <= 0 or speed <= 0 or time_step <= 0
        or steps < 1 or cells <= 0
    ):
        raise ValueError("parámetros físicos o temporales fuera de rango")
    systems = read_systems(config, side)
    etas_by_model = {model: model_etas(config, model) for model in models}
    validate_manifest(output_dir, config)

    total = sum(
        len(systems) * len(etas_by_model[model]) * len(seeds)
        for model in models
    )
    completed = 0
    skipped = 0
    for model in models:
        for system in systems:
            density = system["density"]
            for eta in etas_by_model[model]:
                for seed in seeds:
                    stem = (
                        f"{model}-rho{tag(density)}"
                        f"-eta{tag(eta)}-seed{seed}"
                    )
                    observations = output_dir / f"{stem}-observables.csv"
                    if observations.exists() and not arguments.force:
                        if not observations_are_complete(
                            observations,
                            model=model,
                            density=density,
                            particle_count=system["particle_count"],
                            side=side,
                            cells=cells,
                            cutoff=cutoff,
                            speed=speed,
                            time_step=time_step,
                            eta=eta,
                            seed=seed,
                            steps=steps,
                        ):
                            raise ValueError(
                                f"{observations} está incompleto o es incompatible; "
                                "use --force para regenerar la configuración"
                            )
                        skipped += 1
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
                        "--observables", str(observations),
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
