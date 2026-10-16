"""TP4 2.2: barrido de posiciones, control numerico y checkpoints por corrida."""
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

from billiard_analysis import frames, Energy, energy_series, maximum_relative_error
from performance_analysis import conversion_times
from position_analysis import used_fraction, summarize_positions

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "python/.matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / "python/.cache"))
import matplotlib
import matplotlib.pyplot as plt


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    config_path = ROOT / "experiments/configs/obstacle-position.json"
    config = json.loads(config_path.read_text())
    binary = ROOT / "cpp/build/release/tp4"
    if not binary.exists(): raise ValueError("Compilar primero: make release")
    sources = [ROOT / "cpp/src/main.cpp", *sorted((ROOT / "cpp/include").rglob("*.hpp")),
               Path(__file__), ROOT / "python/position_analysis.py", ROOT / "python/billiard_analysis.py",
               ROOT / "python/performance_analysis.py"]
    contract = dict(config=config, binary_sha256=digest(binary),
                    source_sha256={str(p.relative_to(ROOT)):digest(p) for p in sources},
                    python=sys.version, numpy=np.__version__, matplotlib=matplotlib.__version__,
                    platform=platform.platform())
    fingerprint = hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
    results = ROOT / "experiments/results"
    raw = ROOT / "experiments/raw/obstacle-position"
    figures = ROOT / "experiments/figures"
    checkpoints = results / "position-cases"
    for p in [results, raw, figures, checkpoints]: p.mkdir(parents=True, exist_ok=True)
    contract_path = results / "position-contract.json"
    if contract_path.exists() and json.loads(contract_path.read_text())["fingerprint"] != fingerprint:
        raise ValueError("Fuentes o configuracion cambiaron; no mezclar checkpoints")
    contract_path.write_text(json.dumps(dict(fingerprint=fingerprint, **contract),indent=2)+"\n")

    def simulate(name, n, x, seed, dt, interval):
        path = raw / (name+".csv")
        command = [str(binary), "billiard", "--n", str(n), "--seed", str(seed),
            "--duration", str(config["duration"]), "--dt", str(dt),
            "--save-every", str(round(interval/dt)), "--obstacles", "1", "--obstacle-x", str(x),
            "--output", str(path)]
        p = subprocess.run(command, capture_output=True, text=True)
        if p.returncode: raise RuntimeError(name+": "+p.stderr)
        metadata = json.loads(Path(str(path)+".json").read_text())
        return path, metadata, [str(binary.relative_to(ROOT)), *command[1:-1],str(path.relative_to(ROOT))]

    # Pilotos completos en los extremos. Se conservan resultados y una huella para reanudar.
    pilot_path = results / "position-step-validation.json"
    if pilot_path.exists():
        pilot = json.loads(pilot_path.read_text())
        if pilot["fingerprint"] != fingerprint: raise ValueError("Piloto incompatible")
        dt = pilot["study_dt"]
    else:
        pilot_runs = []
        dt = config["pilot_start_dt"]
        for attempt in range(4):
            ok = True
            for n in config["particle_counts"]:
                for side, x in [("center", config["positions_m"][0]), ("wall", config["positions_m"][-1])]:
                    name = f"pilot-n{n}-{side}-dt{dt:g}"
                    print(name, flush=True)
                    path, meta, command = simulate(name,n,x,1,dt,config["pilot_save_interval"])
                    series = energy_series(path,meta)
                    error = maximum_relative_error(series)
                    series_path = results / (name+"-energy.csv")
                    np.savetxt(series_path,series,delimiter=",",comments="",
                        header="step,time_s,kinetic_J,pair_potential_J,wall_potential_J,obstacle_potential_J,total_J")
                    pilot_runs.append(dict(n=n,x=x,dt=dt,error=error,command=command,
                        trajectory=str(path.relative_to(ROOT)),sha256=digest(path),
                        series=str(series_path.relative_to(ROOT)),series_sha256=digest(series_path)))
                    print(f"  error energetico maximo muestreado={error:.6g}",flush=True)
                    ok = ok and error <= config["relative_energy_tolerance"]
            if ok: break
            dt /= 2
        else: raise RuntimeError("Los pilotos no validan un paso temporal")
        # Margen numerico ante mayor horizonte y posiciones intermedias.
        dt *= config["study_dt_factor"]
        pilot = dict(fingerprint=fingerprint,study_dt=dt,runs=pilot_runs,
            policy="mitad del mayor paso validado en pilotos de 100 s en ambos extremos y ambos N")
        pilot_path.write_text(json.dumps(pilot,indent=2)+"\n")
    print(f"Paso uniforme del estudio: {dt:g} s",flush=True)

    cases=[]
    for n in config["particle_counts"]:
        for index,x in enumerate(config["positions_m"]):
            for seed in config["seeds"]:
                name=f"n{n}-x{index:02d}-seed{seed}"
                stored=checkpoints/(name+".json")
                if stored.exists():
                    case=json.loads(stored.read_text())
                    if case["fingerprint"]!=fingerprint or case["dt"]!=dt: raise ValueError("Checkpoint incompatible")
                    if digest(ROOT/case["trajectory"])!=case["trajectory_sha256"]: raise ValueError("Trayectoria alterada")
                    cases.append(case);continue
                path,meta,command=simulate(name,n,x,seed,dt,config["duration"])
                snapshots=list(frames(path,meta));initial=snapshots[0][2];final=snapshots[-1][2]
                calc=Energy(meta);e0=sum(calc.components(initial));ef=sum(calc.components(final))
                error=abs(ef/e0-1)
                if error>config["relative_energy_tolerance"]:
                    raise RuntimeError(f"{name}: error energetico final {error}; revisar paso y conservar datos")
                case=dict(fingerprint=fingerprint,n=n,obstacle_x=x,seed=seed,dt=dt,duration=config["duration"],
                    conversion=conversion_times(final,dt,config["duration"]),first_contacts=final[:,8].astype(int).tolist(),
                    energy_final_relative_error=error,trajectory=str(path.relative_to(ROOT)),trajectory_sha256=digest(path),
                    metadata=meta,command=command)
                stored.write_text(json.dumps(case,indent=2)+"\n");cases.append(case)
                print(f"{name}: t90={case['conversion']['t90_s']}; Fu final={case['conversion']['fu_final']:.3f}",flush=True)

    summary=summarize_positions(cases)
    write_csv(results/"position-summary.csv",summary)
    write_csv(results/"position-raw.csv",[dict(n=c["n"],obstacle_x_m=c["obstacle_x"],seed=c["seed"],
        t90_s=c["conversion"]["t90_s"],fu_final=c["conversion"]["fu_final"],
        energy_final_relative_error=c["energy_final_relative_error"]) for c in cases])
    grid=np.arange(round(config["duration"]/config["fu_time_interval"])+1)*config["fu_time_interval"]
    fu_rows=[]
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout="constrained",sharey=True)
    for ax,n in zip(axes,config["particle_counts"]):
        for x in config["representative_positions_m"]:
            group=[c for c in cases if c["n"]==n and c["obstacle_x"]==x]
            values=np.array([used_fraction(c["first_contacts"],dt,grid) for c in group])
            mean=values.mean(axis=0);std=values.std(axis=0,ddof=1)
            ax.plot(grid,mean,label=f"x₀={x:g} m")
            ax.fill_between(grid,np.maximum(0,mean-std),np.minimum(1,mean+std),alpha=.12)
            fu_rows.extend(dict(n=n,obstacle_x_m=x,time_s=t,fu_mean=a,fu_std=b) for t,a,b in zip(grid,mean,std))
        ax.set(title=f"N={n} · 5 realizaciones",xlabel="Tiempo (s)",ylim=(0,1.02))
        ax.axhline(.9,color="black",linestyle="--",alpha=.4);ax.legend(fontsize=8);ax.grid(alpha=.2)
    axes[0].set_ylabel("Fracción usada Fᵤ(t) · media ± desvío")
    fig.savefig(figures/"position-fu.png",dpi=180);plt.close(fig)
    write_csv(results/"position-fu.csv",fu_rows)
    fig,ax=plt.subplots(figsize=(8,5),layout="constrained")
    best=[]
    for n,color in [(100,"#0072B2"),(20,"#D55E00")]:
        complete=[r for r in summary if r["n"]==n and r["t90_mean_s"] is not None]
        ax.errorbar([r["obstacle_x_m"] for r in complete],[r["t90_mean_s"] for r in complete],
            yerr=[r["t90_std_s"] for r in complete],fmt="o-",capsize=3,color=color,label=f"N={n}: media ± desvío")
        censored=[r for r in summary if r["n"]==n and r["t90_mean_s"] is None]
        if censored:ax.scatter([r["obstacle_x_m"] for r in censored],[r["t90_mean_lower_bound_s"] for r in censored],
            marker="^",facecolors="none",edgecolors=color,label=f"N={n}: cota inferior")
        if complete:
            b=min(complete,key=lambda r:r["t90_mean_s"])
            best.append(dict(n=n,position_m=b["obstacle_x_m"],mean_s=b["t90_mean_s"],std_s=b["t90_std_s"],
                interpretation="menor media en posiciones muestreadas completas; no optimo exacto ni diferencia estadistica demostrada"))
    ax.set(xlabel="Posición simétrica x₀ (m)",ylabel="t₉₀ (s)",title="Cinco realizaciones por posición · corte 100 s")
    ax.legend();ax.grid(alpha=.2);fig.savefig(figures/"position-t90.png",dpi=180);plt.close(fig)
    (results/"position-best-sampled.json").write_text(json.dumps(best,indent=2)+"\n")
    artifacts=[pilot_path,results/"position-summary.csv",results/"position-raw.csv",results/"position-fu.csv",
               results/"position-best-sampled.json",figures/"position-fu.png",figures/"position-t90.png"]
    manifest=dict(fingerprint=fingerprint,contract=contract,study_dt=dt,
        cases=[dict(path=str((checkpoints/f"n{c['n']}-x{config['positions_m'].index(c['obstacle_x']):02d}-seed{c['seed']}.json").relative_to(ROOT)),
            sha256=digest(checkpoints/f"n{c['n']}-x{config['positions_m'].index(c['obstacle_x']):02d}-seed{c['seed']}.json")) for c in cases],
        artifacts={str(p.relative_to(ROOT)):digest(p) for p in artifacts})
    (results/"position-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(f"Posiciones: {len(cases)} corridas completas. Mejor muestra: {best}",flush=True)


if __name__=="__main__":main()
