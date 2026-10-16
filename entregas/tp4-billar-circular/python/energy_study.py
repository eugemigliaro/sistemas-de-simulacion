"""TP4 2.1.a: barrido, validacion de muestreo y prueba prolongada."""
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

import numpy as np

from billiard_analysis import energy_series, maximum_relative_error

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "python/.matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / "python/.cache"))
import matplotlib
import matplotlib.pyplot as plt


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    config_path = ROOT / "experiments/configs/energy.json"
    config = json.loads(config_path.read_text())
    raw = ROOT / "experiments/raw/energy"
    results = ROOT / "experiments/results"
    figures = ROOT / "experiments/figures"
    for folder in (raw, results, figures):
        folder.mkdir(parents=True, exist_ok=True)
    binary = ROOT / "cpp/build/release/tp4"
    runs, summaries, series_by_dt = [], [], {}

    def run(name, dt, duration, seed, interval):
        steps = round(duration / dt)
        stride = max(1, round(interval / dt))
        path = raw / f"{name}.csv.partial"
        command = [str(binary), "billiard", "--n", str(config["n"]), "--duration", str(duration),
                   "--steps", str(steps), "--save-every", str(stride), "--seed", str(seed),
                   "--obstacles", "0", "--output", str(path)]
        print(f"{name}: N={config['n']}, dt={dt:g} s, tf={duration:g} s", flush=True)
        completed = subprocess.run(command, capture_output=True, text=True)
        replay = [str(binary.relative_to(ROOT)), *command[1:-1], str(path.relative_to(ROOT))]
        if completed.returncode:
            runs.append(dict(name=name, command=replay, status="failed", error=completed.stderr.strip()))
            print(completed.stderr.strip(), flush=True)
            return None
        metadata_path = Path(str(path) + ".json")
        metadata = json.loads(metadata_path.read_text())
        series = energy_series(path, metadata)
        compressed = raw / f"{name}.csv.gz"
        with path.open("rb") as source, compressed.open("wb") as destination:
            with gzip.GzipFile(filename="", mode="wb", fileobj=destination, mtime=0) as zipped:
                shutil.copyfileobj(source, zipped)
        path.unlink()
        final_metadata = raw / f"{name}.json"
        metadata_path.replace(final_metadata)
        series_path = results / f"energy-{name}.csv"
        np.savetxt(series_path, series, delimiter=",", comments="",
                   header="step,time_s,kinetic_J,pair_potential_J,wall_potential_J,obstacle_potential_J,total_J")
        error = maximum_relative_error(series)
        runs.append(dict(name=name, command=replay, status="ok", config=metadata,
                         trajectory=str(compressed.relative_to(ROOT)), trajectory_sha256=digest(compressed),
                         series=str(series_path.relative_to(ROOT)), series_sha256=digest(series_path),
                         metadata=str(final_metadata.relative_to(ROOT)), metadata_sha256=digest(final_metadata),
                         max_relative_error=error))
        print(f"  error maximo muestreado={error:.6g}", flush=True)
        return series

    def sweep(dt):
        name = "dt-" + format(dt, ".9g")
        series = run(name, dt, config["duration"], config["seed"], max(dt, config["save_interval"]))
        error = maximum_relative_error(series) if series is not None else float("inf")
        summaries.append(dict(dt_s=dt, max_relative_error=error, status="ok" if series is not None else "failed"))
        if series is not None:
            series_by_dt[dt] = series

    for dt in config["dt_values"]:
        sweep(dt)
    tolerance = config["relative_tolerance"]
    validation = None
    selected = None
    # Verificar de mayor a menor; si falla una validacion, pasar al candidato siguiente.
    for extension in range(4):
        for dt in sorted(series_by_dt, reverse=True):
            if any(r["max_relative_error"] > tolerance for r in summaries if r["dt_s"] <= dt):
                continue
            name = format(dt, ".9g")
            dense = run("dense-" + name, dt, config["dense_duration"], config["seed"], dt)
            other = run("seed2-" + name, dt, config["duration"], config["validation_seed"], max(dt, config["save_interval"]))
            long = run("long-" + name, dt, config["long_duration"], config["seed"], max(dt, config["long_save_interval"]))
            if dense is None or other is None or long is None:
                continue
            stride = max(1, round(config["save_interval"] / dt))
            dense_error = maximum_relative_error(dense)
            sampled_error = maximum_relative_error(dense[::stride])
            sampling_gap = dense_error - sampled_error
            passed = (max(dense_error, maximum_relative_error(other), maximum_relative_error(long)) <= tolerance
                      and sampling_gap <= tolerance * .1)
            validation = dict(dt=dt, dense_error=dense_error, subsampled_error=sampled_error,
                              sampling_gap=sampling_gap, validation_seed_error=maximum_relative_error(other),
                              long_error=maximum_relative_error(long), passed=passed)
            if passed:
                selected = dt
                break
        if selected is not None:
            break
        if extension < 3:
            sweep(min(r["dt_s"] for r in summaries) / 2)

    summary_path = results / "energy-summary.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["dt_s", "max_relative_error", "status"])
        writer.writeheader()
        writer.writerows(sorted(summaries, key=lambda r: r["dt_s"]))
    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    for dt, series in sorted(series_by_dt.items(), reverse=True):
        ax.plot(series[:, 1], series[:, -1], label=f"Δt={dt:g} s", linewidth=1)
    ax.set(xlabel="Tiempo (s)", ylabel="Energía total (J)", title=f"Sin obstáculos · N={config['n']}")
    ax.legend(fontsize=9)
    ax.grid(alpha=.2)
    fig.savefig(figures / "billiard-energy-time.png", dpi=180)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5), layout="constrained")
    finite = sorted([r for r in summaries if np.isfinite(r["max_relative_error"])], key=lambda r: r["dt_s"])
    ax.loglog([r["dt_s"] for r in finite], [r["max_relative_error"] for r in finite], "o-")
    ax.axhline(tolerance, color="black", linestyle="--", label=f"Criterio: {100*tolerance:g} %")
    ax.set(xlabel="Paso de integración Δt (s)", ylabel="máx |E(t) − E(0)| / E(0)",
           title=f"N={config['n']} · horizonte {config['duration']:g} s")
    ax.grid(True, which="both", alpha=.2)
    ax.legend()
    fig.savefig(figures / "billiard-energy-error.png", dpi=180)
    plt.close(fig)
    selection_path = results / "billiard-step-selection.json"
    selection_path.write_text(json.dumps(dict(selected_dt=selected, relative_tolerance=tolerance,
        status="validated" if selected is not None else "no validated step", validation=validation,
        limitations="Dos condiciones iniciales N=300 sin obstaculos; no garantiza igual error para otras densidades."), indent=2) + "\n")
    sources = [ROOT / "Makefile", ROOT / "cpp/src/main.cpp", *sorted((ROOT / "cpp/include").rglob("*.hpp")),
               ROOT / "python/billiard_analysis.py", ROOT / "python/energy_study.py"]
    artifacts = [summary_path, selection_path, figures / "billiard-energy-time.png", figures / "billiard-energy-error.png"]
    manifest = dict(schema_version=1, config=config, config_sha256=digest(config_path),
        binary_sha256=digest(binary), source_sha256={str(p.relative_to(ROOT)): digest(p) for p in sources},
        platform=platform.platform(), machine=platform.machine(), python=sys.version,
        numpy=np.__version__, matplotlib=matplotlib.__version__,
        compiler=subprocess.check_output([os.environ.get("CXX", "c++"), "--version"], text=True).strip(),
        command_working_directory="raiz TP4; salidas .partial validadas y comprimidas posteriormente",
        runs=runs, artifacts={str(p.relative_to(ROOT)): digest(p) for p in artifacts})
    (results / "energy-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Paso seleccionado: {selected}", flush=True)
    if selected is None:
        raise RuntimeError("No se encontro paso validado; revisar resultados antes de continuar")


if __name__ == "__main__":
    main()
