#!/usr/bin/env python3
"""Ejecuta y resume los experimentos reproducibles del TP3.

Los datos voluminosos quedan en ``experiments/raw`` y ``data/generated``
(ignorados por Git). Las tablas resumen, el plan de búsqueda y la selección
final quedan en ``experiments/results``.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "cpp/build/release/tp3"
RAW = ROOT / "experiments/raw"
RESULTS = ROOT / "experiments/results"
GENERATED_CONFIGS = RAW / "configs"
FINAL_CONFIG = ROOT / "experiments/configs/SdS_TP3_2026Q2G07CS_Config.txt"
PYTHON_SRC = ROOT / "python/src"

sys.path.insert(0, str(PYTHON_SRC))

from tp3analysis.diffusion import summarize_diffusion  # noqa: E402
from tp3analysis.goals import time_to_fraction  # noqa: E402
from tp3analysis.msd import trajectory_msd  # noqa: E402
from tp3analysis.trajectory import read_trajectory  # noqa: E402


RUNTIME_NS = (10, 25, 50, 75, 100, 150, 200, 300, 400)
RUNTIME_REPETITIONS = 10
SEARCH_REPETITIONS = 15
DIFFUSION_REPETITIONS = 5
SEARCH_X = (0.30, 0.40, 0.50, 0.60)
SEARCH_RADII = (0.05, 0.10, 0.15, 0.20, 0.25, 0.28, 0.30, 0.32, 0.33, 0.34)
SEARCH_TMAX = 100.0
DIFFUSION_TMAX = 8.0
DIFFUSION_WINDOW = (0.30, 1.50)
DIFFUSION_MAX_LAG = 3.0
DIFFUSION_BIN_WIDTH = 0.05
DIFFUSION_SAVE_EVERY = 20

RUNTIME_PATTERN = re.compile(
    r"engine (?P<engine>\w+) particles (?P<n>\d+) seed (?P<seed>\d+) "
    r"events (?P<events>\d+) frames (?P<frames>\d+) "
    r"final_time (?P<final_time>[0-9.eE+-]+) "
    r"runtime_seconds (?P<runtime>[0-9.eE+-]+)"
)


@dataclass(frozen=True)
class Configuration:
    label: str
    x: float | None
    y: float | None
    radius: float | None

    @property
    def is_empty(self) -> bool:
        return self.radius is None

    @property
    def path(self) -> Path | None:
        return None if self.is_empty else GENERATED_CONFIGS / f"{self.label}.txt"


def configurations() -> list[Configuration]:
    values = [Configuration("vacia", None, None, None)]
    values.extend(
        Configuration(f"x{int(x * 100):02d}_r{int(radius * 100):02d}", x, 0.34, radius)
        for x in SEARCH_X
        for radius in SEARCH_RADII
        # Se excluye tocar las paredes cortas porque podria tapar un arco. La
        # tangencia con las paredes largas sigue estando enteramente dentro
        # del dominio y la validacion geometrica del motor la admite.
        if radius < x and radius < 1.20 - x and radius <= 0.34
    )
    return values


def prepare() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    GENERATED_CONFIGS.mkdir(parents=True, exist_ok=True)
    (ROOT / "data/generated").mkdir(parents=True, exist_ok=True)
    if not ENGINE.exists():
        subprocess.run(["make", "release"], cwd=ROOT, check=True)
    for config in configurations():
        if config.path is not None:
            config.path.write_text(
                f"{config.x:.2f} {config.y:.2f} {config.radius:.2f}\n",
                encoding="utf-8",
            )
    with (RESULTS / "search_plan.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(("label", "x_m", "y_m", "radius_m"))
        for config in configurations():
            writer.writerow((
                config.label,
                "" if config.x is None else config.x,
                "" if config.y is None else config.y,
                "" if config.radius is None else config.radius,
            ))


def simulate(
    particle_count: int,
    seed: int,
    max_time: float,
    output: Path | str,
    config: Configuration | None = None,
    save_every: int = 0,
    engine: str = "queue",
) -> dict[str, str]:
    command = [
        str(ENGINE), "simulate",
        "--n", str(particle_count),
        "--seed", str(seed),
        "--tmax", str(max_time),
        "--save-every", str(save_every),
        "--engine", engine,
        "--output", str(output),
    ]
    if config is not None and config.path is not None:
        command.extend(("--config", str(config.path)))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    match = RUNTIME_PATTERN.search(result.stderr)
    if match is None:
        raise RuntimeError(f"salida del motor inesperada: {result.stderr!r}")
    return match.groupdict()


def write_rows(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_runtime() -> None:
    rows: list[dict[str, object]] = []
    for particle_count in RUNTIME_NS:
        for repetition in range(RUNTIME_REPETITIONS):
            seed = 1000 + repetition
            report = simulate(particle_count, seed, 30.0, os.devnull)
            rows.append({
                "particle_count": particle_count,
                "seed": seed,
                "engine": report["engine"],
                "events": int(report["events"]),
                "runtime_seconds": float(report["runtime"]),
            })
            print(f"runtime N={particle_count} semilla={seed}", flush=True)
    write_rows(
        RESULTS / "runtime.csv",
        ("particle_count", "seed", "engine", "events", "runtime_seconds"),
        rows,
    )


def _summary(values: list[float]) -> tuple[float, float, float]:
    mean = statistics.fmean(values)
    std = statistics.stdev(values) if len(values) > 1 else math.nan
    sem = std / math.sqrt(len(values)) if len(values) > 1 else math.nan
    return mean, std, sem


def run_search() -> None:
    rows: list[dict[str, object]] = []
    for config in configurations():
        directory = RAW / "search" / config.label
        directory.mkdir(parents=True, exist_ok=True)
        for repetition in range(SEARCH_REPETITIONS):
            seed = 2000 + repetition
            output = directory / f"seed{seed}.txt"
            if not output.exists():
                simulate(100, seed, SEARCH_TMAX, output, config)
            result = time_to_fraction(read_trajectory(output))
            rows.append({
                "label": config.label,
                "x_m": "" if config.x is None else config.x,
                "radius_m": "" if config.radius is None else config.radius,
                "seed": seed,
                "reached": int(result.reached),
                "t90_seconds": "" if result.t90 is None else result.t90,
                "goals_at_end": result.goals_at_end,
            })
            print(f"busqueda {config.label} semilla={seed}", flush=True)

    fields = (
        "label", "x_m", "radius_m", "seed", "reached", "t90_seconds",
        "goals_at_end",
    )
    write_rows(RESULTS / "t90_runs.csv", fields, rows)

    summaries: list[dict[str, object]] = []
    for config in configurations():
        selected = [row for row in rows if row["label"] == config.label]
        reached = [float(row["t90_seconds"]) for row in selected if row["reached"]]
        mean, std, sem = _summary(reached)
        goals = [float(row["goals_at_end"]) for row in selected]
        summaries.append({
            "label": config.label,
            "x_m": "" if config.x is None else config.x,
            "radius_m": "" if config.radius is None else config.radius,
            "realizations": len(selected),
            "reached": len(reached),
            "mean_t90_seconds": mean,
            "std_t90_seconds": std,
            "sem_t90_seconds": sem,
            "mean_goals_at_end": statistics.fmean(goals),
        })
    write_rows(
        RESULTS / "t90_summary.csv",
        (
            "label", "x_m", "radius_m", "realizations", "reached",
            "mean_t90_seconds", "std_t90_seconds", "sem_t90_seconds",
            "mean_goals_at_end",
        ),
        summaries,
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def select_best() -> tuple[Configuration, dict[str, str]]:
    rows = _read_csv(RESULTS / "t90_summary.csv")
    eligible = [
        row for row in rows
        if row["label"] != "vacia" and int(row["reached"]) == int(row["realizations"])
    ]
    best_row = min(eligible, key=lambda row: float(row["mean_t90_seconds"]))
    config = next(value for value in configurations() if value.label == best_row["label"])
    return config, best_row


def run_diffusion() -> None:
    run_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    for config in configurations():
        directory = RAW / "diffusion" / config.label
        directory.mkdir(parents=True, exist_ok=True)
        curves = []
        for repetition in range(DIFFUSION_REPETITIONS):
            seed = 3000 + repetition
            output = directory / f"seed{seed}.txt"
            if not output.exists():
                simulate(
                    100, seed, DIFFUSION_TMAX, output, config,
                    save_every=DIFFUSION_SAVE_EVERY,
                )
            curve = trajectory_msd(
                read_trajectory(output), DIFFUSION_BIN_WIDTH, DIFFUSION_MAX_LAG
            )
            curves.append(curve)
            print(f"difusion {config.label} semilla={seed}", flush=True)
        summary = summarize_diffusion(curves, DIFFUSION_WINDOW)
        for repetition, fit in enumerate(summary.per_run):
            run_rows.append({
                "label": config.label,
                "seed": 3000 + repetition,
                "D_m2_s": fit.coefficient,
                "fit_error_m2_s": fit.error,
            })
        summary_rows.append({
            "label": config.label,
            "mean_D_m2_s": summary.plain.mean,
            "std_D_m2_s": summary.plain.std,
            "sem_D_m2_s": summary.plain.sem,
            "pooled_D_m2_s": summary.pooled.coefficient,
            "pooled_fit_error_m2_s": summary.pooled.error,
            "realizations": DIFFUSION_REPETITIONS,
        })
        write_rows(
            RESULTS / f"msd_{config.label}.csv",
            ("lag_seconds", "msd_m2", "std_m2"),
            [
                {"lag_seconds": lag, "msd_m2": msd, "std_m2": std}
                for lag, msd, std in zip(
                    summary.pooled_curve.lags,
                    summary.pooled_curve.msd,
                    summary.pooled_curve.std,
                )
            ],
        )
        write_rows(
            RESULTS / f"ec_{config.label}.csv",
            ("slope_m2_s", "squared_error"),
            [
                {"slope_m2_s": slope, "squared_error": error}
                for slope, error in zip(
                    summary.pooled.fit.sweep_c,
                    summary.pooled.fit.sweep_error,
                )
            ],
        )
    write_rows(
        RESULTS / "diffusion_runs.csv",
        ("label", "seed", "D_m2_s", "fit_error_m2_s"),
        run_rows,
    )
    write_rows(
        RESULTS / "diffusion_summary.csv",
        (
            "label", "mean_D_m2_s", "std_D_m2_s", "sem_D_m2_s",
            "pooled_D_m2_s", "pooled_fit_error_m2_s", "realizations",
        ),
        summary_rows,
    )


def run_display_runs() -> None:
    best, best_row = select_best()
    FINAL_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    assert best.path is not None
    shutil.copyfile(best.path, FINAL_CONFIG)

    runs = _read_csv(RESULTS / "t90_runs.csv")
    display: dict[str, object] = {
        "best": {
            **asdict(best),
            "mean_t90_seconds": float(best_row["mean_t90_seconds"]),
            "std_t90_seconds": float(best_row["std_t90_seconds"]),
            "sem_t90_seconds": float(best_row["sem_t90_seconds"]),
        },
        "diffusion_window_seconds": list(DIFFUSION_WINDOW),
    }
    for role, config in (("vacia", configurations()[0]), ("mejor", best)):
        candidates = [row for row in runs if row["label"] == config.label and row["reached"] == "1"]
        mean = statistics.fmean(float(row["t90_seconds"]) for row in candidates)
        chosen = min(candidates, key=lambda row: abs(float(row["t90_seconds"]) - mean))
        seed = int(chosen["seed"])
        output = ROOT / "data/generated" / f"anim_{role}.txt"
        simulate(100, seed, 30.0, output, config, save_every=20)
        display[role] = {
            "label": config.label,
            "seed": seed,
            "trajectory": str(output.relative_to(ROOT)),
            "t90_seconds": float(chosen["t90_seconds"]),
            "search_trajectory": str(
                (RAW / "search" / config.label / f"seed{seed}.txt").relative_to(ROOT)
            ),
        }
    (RESULTS / "selection.json").write_text(
        json.dumps(display, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage", choices=("runtime", "search", "diffusion", "display", "all")
    )
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    prepare()
    stages = (
        ("runtime", run_runtime),
        ("search", run_search),
        ("diffusion", run_diffusion),
        ("display", run_display_runs),
    )
    for name, function in stages:
        if arguments.stage in (name, "all"):
            function()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
