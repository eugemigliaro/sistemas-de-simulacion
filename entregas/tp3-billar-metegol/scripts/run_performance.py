#!/usr/bin/env python3
"""Ejecuta y resume el experimento de rendimiento del punto 1.1."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shlex
import subprocess
from pathlib import Path

from tp3analysis.performance import parse_engine_report, summarize_performance


RAW_FIELDS = (
    "engine",
    "particle_count",
    "seed",
    "max_time",
    "events",
    "frames",
    "final_time",
    "runtime_seconds",
    "command",
)
SUMMARY_FIELDS = (
    "engine",
    "particle_count",
    "max_time",
    "repetitions",
    "runtime_mean_s",
    "runtime_std_s",
    "runtime_sem_s",
    "runtime_min_s",
    "runtime_max_s",
    "events_mean",
    "frames_mean",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta las repeticiones de tiempo vs. N del TP3."
    )
    parser.add_argument("config", type=Path)
    parser.add_argument(
        "--force",
        action="store_true",
        help="descarta mediciones anteriores para esta configuración",
    )
    return parser.parse_args()


def require_unique_int_list(config: dict, key: str, *, minimum: int) -> list[int]:
    value = config.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} debe ser una lista no vacía")
    result = [int(item) for item in value]
    if any(item < minimum for item in result) or len(result) != len(set(result)):
        raise ValueError(f"{key} contiene valores inválidos o repetidos")
    return result


def normalized_manifest(config: dict) -> str:
    relevant = {
        "schema_version": 1,
        "binary": config.get("binary", "cpp/build/release/tp3"),
        "engine": config.get("engine", "queue"),
        "particle_counts": config["particle_counts"],
        "seeds": config["seeds"],
        "max_time": config.get("max_time", 30),
    }
    return json.dumps(relevant, indent=2, sort_keys=True) + "\n"


def validate_manifest(path: Path, config: dict, *, force: bool) -> None:
    expected = normalized_manifest(config)
    if path.exists() and path.read_text(encoding="utf-8") != expected and not force:
        raise ValueError(
            f"{path} pertenece a otra configuración; use --force o cambie las salidas"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8")


def read_raw(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != RAW_FIELDS:
            raise ValueError(f"cabecera incompatible en {path}")
        return list(reader)


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summarize_performance(rows))
    temporary.replace(path)


def append_raw(path: Path, row: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    with path.open("a", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=RAW_FIELDS)
        if not existed:
            writer.writeheader()
        writer.writerow(row)
        target.flush()


def main() -> int:
    arguments = parse_args()
    config_path = arguments.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    root = config_path.parents[2]

    binary_setting = str(config.get("binary", "cpp/build/release/tp3"))
    binary = root / binary_setting
    if not binary.is_file():
        raise ValueError(f"no existe el motor release: {binary}")
    engine = str(config.get("engine", "queue"))
    if engine not in {"queue", "naive"}:
        raise ValueError("engine debe ser queue o naive")
    particle_counts = require_unique_int_list(config, "particle_counts", minimum=1)
    seeds = require_unique_int_list(config, "seeds", minimum=0)
    max_time = float(config.get("max_time", 30))
    if max_time <= 0 or not math.isfinite(max_time):
        raise ValueError("max_time debe ser finito y positivo")

    raw_path = root / config.get(
        "raw_output", "experiments/results/performance-raw.csv"
    )
    summary_path = root / config.get(
        "summary_output", "experiments/results/performance-summary.csv"
    )
    manifest_path = root / config.get(
        "manifest_output", "experiments/results/performance-manifest.json"
    )
    if arguments.force:
        for path in (raw_path, summary_path, manifest_path):
            path.unlink(missing_ok=True)
    validate_manifest(manifest_path, config, force=arguments.force)

    rows = read_raw(raw_path)
    completed: dict[tuple[str, int, int, float], dict[str, str]] = {}
    for row in rows:
        key = (
            row["engine"],
            int(row["particle_count"]),
            int(row["seed"]),
            float(row["max_time"]),
        )
        if key in completed:
            raise ValueError(f"medición duplicada en {raw_path}: {key}")
        completed[key] = row

    total = len(particle_counts) * len(seeds)
    reused = 0
    executed = 0
    for particle_count in particle_counts:
        for seed in seeds:
            key = (engine, particle_count, seed, max_time)
            if key in completed:
                reused += 1
                print(f"[{executed + reused}/{total}] reutilizada N={particle_count} seed={seed}")
                continue

            command = [
                str(binary),
                "simulate",
                "--engine",
                engine,
                "--n",
                str(particle_count),
                "--seed",
                str(seed),
                "--tmax",
                f"{max_time:.17g}",
                "--output",
                os.devnull,
            ]
            process = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
            if process.returncode != 0:
                raise RuntimeError(
                    f"falló N={particle_count}, seed={seed}: {process.stderr.strip()}"
                )
            report = parse_engine_report(process.stderr)
            if (
                report.engine != engine
                or report.particle_count != particle_count
                or report.seed != seed
                or not math.isclose(report.final_time, max_time, abs_tol=1e-9)
            ):
                raise ValueError(
                    "el resumen del motor no coincide con la corrida solicitada: "
                    f"{report}"
                )
            row = {
                "engine": report.engine,
                "particle_count": str(report.particle_count),
                "seed": str(report.seed),
                "max_time": f"{max_time:.17g}",
                "events": str(report.events),
                "frames": str(report.frames),
                "final_time": f"{report.final_time:.17g}",
                "runtime_seconds": f"{report.runtime_seconds:.17g}",
                "command": shlex.join([binary_setting, *command[1:]]),
            }
            append_raw(raw_path, row)
            rows.append(row)
            completed[key] = row
            executed += 1
            print(
                f"[{executed + reused}/{total}] N={particle_count} seed={seed} "
                f"runtime={report.runtime_seconds:.6g}s",
                flush=True,
            )

    selected_rows = [
        completed[(engine, particle_count, seed, max_time)]
        for particle_count in particle_counts
        for seed in seeds
    ]
    write_summary(summary_path, selected_rows)
    print(
        f"Rendimiento terminado: {executed} ejecutadas, {reused} reutilizadas.\n"
        f"Crudo: {raw_path}\nResumen: {summary_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
