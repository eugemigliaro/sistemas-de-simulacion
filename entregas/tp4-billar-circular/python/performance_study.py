"""2.1.b y 2.4.a: corrida secuencial, checkpoints y comparacion recalculada."""
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

from benchmark_build import build, ROOT, TP3
from billiard_analysis import frames, Energy
from performance_analysis import conversion_times, summarize, summarize_density

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "python/.matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / "python/.cache"))
import matplotlib
import matplotlib.pyplot as plt


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    config_path = ROOT / "experiments/configs/performance.json"
    config = json.loads(config_path.read_text())
    binary, cpp_sources, build_command = build()
    steps = round(config["duration"] / config["dt"])
    sources = [*cpp_sources, *sorted((ROOT / "cpp/include").rglob("*.hpp")),
               *sorted((TP3 / "cpp/include/tp3").glob("*.hpp")), Path(__file__),
               ROOT / "python/performance_analysis.py", ROOT / "python/benchmark_build.py",
               ROOT / "python/billiard_analysis.py"]
    cpu = os.environ.get("TP4_CPU_DESCRIPTION", "").strip()
    if not cpu:
        probe = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True)
        if probe.returncode:
            raise RuntimeError("No se pudo identificar CPU; indicar TP4_CPU_DESCRIPTION tras verificar el hardware")
        cpu = probe.stdout.strip()
    contract = dict(config=config, source_sha256={os.path.relpath(p, ROOT): digest(p) for p in sources},
                    platform=platform.platform(), cpu=cpu, machine=platform.machine(),
                    compiler=subprocess.check_output([os.environ.get("CXX", "c++"), "--version"], text=True).strip(),
                    timing="steady_clock around simulation kernel; initialization and all file I/O excluded; sequential runs",
                    tp4_output="initial and final states; per-particle first_contact_step retains conversion history")
    fingerprint = hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()
    raw = ROOT / "experiments/raw/performance"
    results = ROOT / "experiments/results"
    figures = ROOT / "experiments/figures"
    for folder in [raw, results, figures]: folder.mkdir(parents=True, exist_ok=True)
    checkpoint = results / "performance-cases"
    checkpoint.mkdir(exist_ok=True)
    contract_path = results / "performance-contract.json"
    if contract_path.exists() and json.loads(contract_path.read_text())["fingerprint"] != fingerprint:
        raise ValueError("El protocolo o las fuentes cambiaron: conservar checkpoints y usar otro directorio de resultados")
    contract_path.write_text(json.dumps(dict(fingerprint=fingerprint, **contract), indent=2) + "\n")
    cases = []
    # Toda medicion es secuencial. No paralelizar motores ni post-procesos costosos.
    for engine in ["tp4", "tp3"]:
        for n in config[engine + "_counts"]:
            for seed in config["seeds"]:
                name = f"{engine}-n{n}-seed{seed}"
                stored = checkpoint / (name + ".json")
                if stored.exists():
                    case = json.loads(stored.read_text())
                    if case["fingerprint"] != fingerprint: raise ValueError("Checkpoint incompatible")
                    if engine == "tp4" and digest(ROOT / case["trajectory"]) != case["trajectory_sha256"]:
                        raise ValueError("Trayectoria de checkpoint alterada")
                    cases.append(case)
                    continue
                path = raw / (name + ".csv")
                command = [str(binary), engine, str(n), str(seed), str(config["duration"]), str(steps),
                           str(config["dense_sweeps"]), str(path)]
                process = subprocess.run(command, capture_output=True, text=True)
                if process.returncode: raise RuntimeError(f"{name}: {process.stderr}")
                report = json.loads(process.stdout)
                if abs(report["final_time"] - config["duration"]) > 1e-9 or report["runtime_seconds"] <= 0:
                    raise ValueError("Cronometro o horizonte invalido")
                case = dict(fingerprint=fingerprint, engine=engine, n=n, seed=seed,
                    command=[str(binary.relative_to(ROOT)), *command[1:-1], str(path.relative_to(ROOT))], **report)
                if engine == "tp4":
                    meta = dict(n=n, duration=config["duration"], steps=steps, save_every=steps,
                        dt=config["duration"] / steps, radius=.51, particle_radius=.0175,
                        mass=.025, stiffness=10000, obstacles=True, obstacle_x=.0175)
                    states = list(frames(path, meta))
                    initial, final = states[0][2], states[-1][2]
                    case["conversion"] = conversion_times(final, meta["dt"], config["duration"])
                    calculator = Energy(meta)
                    e0 = sum(calculator.components(initial)); ef = sum(calculator.components(final))
                    case["final_energy_relative_error"] = abs(ef / e0 - 1)
                    if case["final_energy_relative_error"] > config["relative_energy_tolerance"]:
                        raise ValueError(f"{name}: error energetico final {case['final_energy_relative_error']}; revisar dt antes de medir")
                    case.update(trajectory=str(path.relative_to(ROOT)), trajectory_sha256=digest(path), metadata=meta,
                                initialization="hexagonal + Monte Carlo" if n > 400 else "sequential area-uniform rejection")
                    Path(str(path) + ".json").write_text(json.dumps(meta, indent=2) + "\n")
                else:
                    case["initialization"] = "original TP3 random rejection" if n <= 400 else "original TP3 triangular"
                stored.write_text(json.dumps(case, indent=2) + "\n")
                cases.append(case)
                print(f"{name}: {report['runtime_seconds']:.6g} s", flush=True)
    summary = summarize(cases)
    density = summarize_density(cases)
    write_csv(results / "performance-summary.csv", summary)
    write_csv(results / "density-summary.csv", density)
    per_run = [dict(n=c["n"], seed=c["seed"], **c["conversion"], cutoff_s=c["final_time"])
               for c in cases if c["engine"] == "tp4"]
    write_csv(results / "density-raw.csv", per_run)
    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    for engine, label in [("tp4", "TP4 · paso temporal"), ("tp3", "TP3 · eventos")]:
        group = sorted([r for r in summary if r["engine"] == engine], key=lambda r: r["n"])
        ax.errorbar([r["n"] for r in group], [r["runtime_mean_s"] for r in group],
                    yerr=[r["runtime_std_s"] for r in group], marker="o", capsize=3, label=label)
    ax.set(xscale="log", yscale="log", xlabel="Número de partículas N", ylabel="Tiempo de simulación (s)",
           title="tf=30 s · media ± desvío estándar · 10 realizaciones")
    ax.legend(); ax.grid(True, which="both", alpha=.2)
    fig.savefig(figures / "runtime-comparison.png", dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    for obs, label in [("t90", "t₉₀"), ("t100", "t₁₀₀")]:
        observed = [r for r in density if r[obs + "_mean_s"] is not None]
        ax.errorbar([r["density_m2"] for r in observed], [r[obs + "_mean_s"] for r in observed],
                    yerr=[r[obs + "_std_s"] for r in observed], marker="o", capsize=3, label=label)
        censored = [r for r in density if r[obs + "_mean_s"] is None]
        if censored:
            ax.scatter([r["density_m2"] for r in censored], [r[obs + "_mean_lower_bound_s"] for r in censored],
                       marker="^", label=f"{label}: cota inferior (censura)")
    ax.set(xlabel="Densidad N/(πR²) (m⁻²)", ylabel="Tiempo de conversión (s)",
           title="Obstáculos en contacto · media ± desvío estándar")
    ax.legend(); ax.grid(alpha=.2)
    fig.savefig(figures / "conversion-vs-density.png", dpi=180); plt.close(fig)
    artifacts = [results / "performance-summary.csv", results / "density-summary.csv", results / "density-raw.csv",
                 figures / "runtime-comparison.png", figures / "conversion-vs-density.png"]
    manifest = dict(fingerprint=fingerprint, contract=contract, binary_sha256=digest(binary),
        build_command=build_command, python=sys.version, numpy=np.__version__, matplotlib=matplotlib.__version__,
        cases=[dict(path=str((checkpoint / f"{c['engine']}-n{c['n']}-seed{c['seed']}.json").relative_to(ROOT)),
                    sha256=digest(checkpoint / f"{c['engine']}-n{c['n']}-seed{c['seed']}.json")) for c in cases],
        artifacts={str(p.relative_to(ROOT)): digest(p) for p in artifacts})
    (results / "performance-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Estudio completo: {len(cases)} corridas; {len(per_run)} salidas reutilizadas para densidad.", flush=True)


if __name__ == "__main__": main()
