"""Ejecuta el barrido completo y conserva su procedencia."""
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

from analysis import load_trajectory, position_errors

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "python/.matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / "python/.cache"))
import matplotlib
import matplotlib.pyplot as plt


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config_path = ROOT / "experiments/configs/oscillator.json"
    config = json.loads(config_path.read_text())
    binary = ROOT / "cpp/build/release/tp4"
    raw = ROOT / "experiments/raw/oscillator"
    results = ROOT / "experiments/results"
    figures = ROOT / "experiments/figures"
    for path in (raw, results, figures):
        path.mkdir(parents=True, exist_ok=True)
    rows, runs = [], []
    for method in config["methods"]:
        for steps in config["steps"]:
            output = raw / f"{method}-{steps}.csv"
            temporary = output.with_suffix(".partial")
            command = [str(binary), "oscillator", "--method", method, "--steps", str(steps)]
            for key in ("mass", "stiffness", "damping", "x0", "v0", "duration"):
                command += ["--" + key, str(config[key])]
            command += ["--output", str(temporary)]
            subprocess.run(command, check=True)
            data = load_trajectory(temporary, config, steps)
            ecm, maximum = position_errors(data, config)
            temporary.replace(output)
            rows.append(dict(method=method, steps=steps, dt_s=config["duration"] / steps,
                             samples=steps, ecm_m2=ecm, max_error_m=maximum))
            replay_command = [str(binary.relative_to(ROOT)), *command[1:-1], str(temporary.relative_to(ROOT))]
            runs.append(dict(method=method, steps=steps, trajectory=str(output.relative_to(ROOT)),
                             sha256=digest(output), command=replay_command))
        print(f"{method}: {len(config['steps'])} trayectorias verificadas", flush=True)
    summary = results / "oscillator-summary.csv"
    with summary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    styles = {
        "beeman": ("Beeman", "o", "-", "#0072B2"),
        "verlet": ("Verlet original", "o", "-", "#D55E00"),
        "velocity-verlet": ("Velocity Verlet", "x", "--", "#009E73"),
        "euler-pc": ("Euler predictor-corrector", "s", "-", "#CC79A7"),
    }
    for method in config["methods"]:
        values = sorted((r for r in rows if r["method"] == method), key=lambda r: r["dt_s"])
        label, marker, line, color = styles[method]
        ax.loglog([r["dt_s"] for r in values], [r["ecm_m2"] for r in values],
                  label=label, marker=marker, linestyle=line, color=color,
                  markerfacecolor="none", linewidth=1.7, markersize=6)
    ax.set(xlabel="Paso de integración Δt (s)", ylabel="ECM de posición (m²)")
    ax.grid(True, which="both", alpha=0.22)
    ax.legend(fontsize=10)
    ax.set_title("Oscilador amortiguado · 0 < t ≤ 5 s", fontsize=13)
    fig.savefig(figures / "oscillator-ecm.png", dpi=200)
    fig.savefig(figures / "oscillator-ecm.svg")
    plt.close(fig)
    sources = [ROOT / "Makefile", *sorted((ROOT / "cpp").rglob("*.cpp")),
               *sorted((ROOT / "cpp/include").rglob("*.hpp")),
               ROOT / "python/analysis.py", ROOT / "python/study.py"]
    manifest = dict(schema_version=1, config=config, config_sha256=digest(config_path),
                    binary_sha256=digest(binary), python=sys.version, numpy=np.__version__,
                    matplotlib=matplotlib.__version__, platform=platform.platform(),
                    machine=platform.machine(),
                    compiler=subprocess.check_output([os.environ.get("CXX", "c++"), "--version"], text=True).strip(),
                    build="make release (ver Makefile y su hash)",
                    source_sha256={str(p.relative_to(ROOT)): digest(p) for p in sources},
                    command_working_directory="raiz del TP4; .partial se renombra a .csv tras validar",
                    averaging="promedio temporal n=1,...,M; t=0 excluido; sin realizaciones aleatorias",
                    runs=runs,
                    artifacts={str(p.relative_to(ROOT)): digest(p) for p in
                               [summary, figures / "oscillator-ecm.png", figures / "oscillator-ecm.svg"]})
    (results / "oscillator-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Estudio terminado: {len(rows)} corridas; {summary.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
