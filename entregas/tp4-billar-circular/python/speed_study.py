"""TP4 2.3: simulación, checkpoints, distribución de rapidez y ajuste térmico."""
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

from billiard_analysis import frames, Energy, maximum_relative_error
from speed_analysis import histogram, mb_bins, fit_theta, stationary_suffix

ROOT=Path(__file__).resolve().parents[1]
SIMULATION_KEYS=["n","seeds","duration","dt","save_interval"]
os.environ.setdefault("MPLBACKEND","Agg")
os.environ.setdefault("MPLCONFIGDIR",str(ROOT/"python/.matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME",str(ROOT/"python/.cache"))
import matplotlib
import matplotlib.pyplot as plt


def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()


def save_json(path,data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+"\n")


def save_csv(path,rows):
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    # --reanalyze recalcula histogramas y ajuste desde las muestras guardadas (p. ej. con
    # otros bins), sin recompilar ni simular: las corridas deben coincidir con la configuracion.
    reanalyze="--reanalyze" in sys.argv[1:]
    c=json.loads((ROOT/"experiments/configs/speed.json").read_text())
    binary=ROOT/"cpp/build/release/tp4"
    results,raw,figures=[ROOT/("experiments/"+s) for s in ["results","raw/speed","figures"]]
    cases_dir=results/"speed-cases"
    for p in [results,raw,figures,cases_dir]: p.mkdir(parents=True,exist_ok=True)
    contract_path=results/"speed-contract.json"
    if reanalyze:
        stored=json.loads(contract_path.read_text())
        if any(stored["config"][k]!=c[k] for k in SIMULATION_KEYS):
            raise ValueError("La configuracion de simulacion no coincide con las corridas guardadas")
        fingerprint=stored["fingerprint"]
    else:
        sources=[ROOT/"cpp/src/main.cpp",*sorted((ROOT/"cpp/include").rglob("*.hpp")),
                 Path(__file__),ROOT/"python/speed_analysis.py",ROOT/"python/billiard_analysis.py"]
        contract=dict(config=c,binary_sha256=digest(binary),
            source_sha256={str(p.relative_to(ROOT)):digest(p) for p in sources},
            python=sys.version,numpy=np.__version__,matplotlib=matplotlib.__version__,platform=platform.platform())
        fingerprint=hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
        if contract_path.exists() and json.loads(contract_path.read_text())["fingerprint"]!=fingerprint:
            raise ValueError("Fuentes/configuracion cambiaron; no mezclar checkpoints")
        save_json(contract_path,dict(fingerprint=fingerprint,**contract))
    cases=[]; all_speeds=[]; all_energy=[]
    for seed in c["seeds"]:
        name=f"seed-{seed:02d}"
        checkpoint=cases_dir/(name+".json")
        samples=cases_dir/(name+".npz")
        if checkpoint.exists():
            case=json.loads(checkpoint.read_text())
            if case["fingerprint"]!=fingerprint or digest(samples)!=case["samples_sha256"]:
                raise ValueError("Checkpoint incompatible/corrupto")
            print(name+" recuperado",flush=True)
        elif reanalyze:
            raise ValueError(name+": falta la corrida; --reanalyze no simula")
        else:
            path=raw/(name+".csv")
            command=[str(binary),"billiard","--n",str(c["n"]),"--seed",str(seed),
                "--duration",str(c["duration"]),"--dt",str(c["dt"]),
                "--save-every",str(round(c["save_interval"]/c["dt"])),
                "--obstacles","0","--output",str(path)]
            print(name+" simulando",flush=True)
            process=subprocess.run(command,capture_output=True,text=True)
            if process.returncode: raise RuntimeError(process.stderr)
            meta=json.loads(Path(str(path)+".json").read_text())
            speeds=[]; energy=[]; times=[]
            calculator=Energy(meta)
            for step,time,state in frames(path,meta):
                speeds.append(np.linalg.norm(state[:,5:7],axis=1))
                components=calculator.components(state)
                times.append(time); energy.append([step,time,*components,sum(components)])
            np.savez_compressed(samples,times=times,speeds=speeds,energy=energy)
            error=maximum_relative_error(np.asarray(energy))
            case=dict(fingerprint=fingerprint,seed=seed,metadata=meta,
                command=[str(binary.relative_to(ROOT)),*command[1:-1],str(path.relative_to(ROOT))],
                trajectory=str(path.relative_to(ROOT)),trajectory_sha256=digest(path),
                samples=str(samples.relative_to(ROOT)),samples_sha256=digest(samples),
                maximum_sampled_relative_energy_error=error)
            save_json(checkpoint,case)
        if case["maximum_sampled_relative_energy_error"]>c["relative_energy_tolerance"]:
            raise ValueError("El paso temporal no satisface la tolerancia energetica")
        with np.load(samples) as data:
            times=data["times"].copy()
            all_speeds.append(data["speeds"].copy()); all_energy.append(data["energy"].copy())
        cases.append(case)

    speeds=np.asarray(all_speeds); energy=np.asarray(all_energy)
    mass=cases[0]["metadata"]["mass"]
    reference=mass*cases[0]["metadata"]["speed"]**2/2
    width=c["bin_width"]
    # Con bin_offset=width/2, v0=1 m/s cae en el centro de un bin: el redondeo de las
    # velocidades de particulas aun sin chocar no reparte la delta inicial entre dos bins.
    first=c.get("bin_offset",0) or width
    edges=np.round(np.r_[0,first+np.arange(int(np.ceil((speeds.max()-first)/width))+2)*width],12)
    centers=(edges[:-1]+edges[1:])/2
    windows=[]; window_hist=[]; window_theta=[]
    for start in np.arange(0,c["duration"],c["window_s"]):
        mask=(times>=start)&(times<start+c["window_s"])
        densities=np.array([histogram(run[mask],edges) for run in speeds])
        theta,sse=fit_theta(densities.mean(axis=0),edges,mass,reference)
        windows.append(dict(start_s=float(start),end_exclusive_s=float(start+c["window_s"]),
            frames_per_run=int(mask.sum()),theta_fit_J=theta,sse=sse))
        window_hist.append(densities.mean(axis=0)); window_theta.append(theta)
    # La primera ventana contiene el estado inicial singular: nunca integrarla
    # al ajuste estacionario aunque su promedio diluya el transitorio.
    start,_,_=stationary_suffix(window_hist[1:],window_theta[1:],edges,
        c["stationarity_tv_limit"],c["stationarity_theta_relative_limit"],c["minimum_window_comparisons"])
    _,tv,relative=stationary_suffix(window_hist,window_theta,edges,
        c["stationarity_tv_limit"],c["stationarity_theta_relative_limit"],c["minimum_window_comparisons"])
    if start is not None: start+=1
    for i in range(1,len(windows)):
        windows[i]["tv_from_previous"]=float(tv[i-1])
        windows[i]["theta_relative_change"]=float(relative[i-1])
    save_csv(results/"speed-windows.csv",[dict(tv_from_previous=None,theta_relative_change=None,**w) if i==0 else w
                                              for i,w in enumerate(windows)])
    if start is None:
        raise ValueError("No se cumple el criterio de estabilidad: extender horizonte con un estudio nuevo")
    stationary_start=windows[start]["start_s"]
    mask=(times>=stationary_start)&(times<c["duration"])
    densities=np.array([histogram(run[mask],edges) for run in speeds])
    mean,sd=densities.mean(axis=0),densities.std(axis=0,ddof=1)
    theta,sse=fit_theta(mean,edges,mass,reference)
    per_run=[]
    for i,seed in enumerate(c["seeds"]):
        fitted,error=fit_theta(densities[i],edges,mass,reference)
        per_run.append(dict(seed=seed,theta_fit_J=fitted,sse=error,
            kinetic_per_particle_J=float(mass*np.mean(speeds[i,mask]**2)/2),
            potential_per_particle_J=float(np.mean(energy[i,mask,3:6].sum(axis=1))/c["n"]),
            total_per_particle_J=float(np.mean(energy[i,mask,-1])/c["n"])))
    save_csv(results/"speed-fit-per-run.csv",per_run)
    save_csv(results/"speed-stationary.csv",[dict(v_left_m_s=float(a),v_right_m_s=float(b),
        density_mean=float(y),density_std=float(s),model_bin_density=float(f))
        for a,b,y,s,f in zip(edges[:-1],edges[1:],mean,sd,mb_bins(edges,mass,theta))])
    snapshots=[]
    for time in c["snapshot_times"]:
        j=int(np.argmin(np.abs(times-time)))
        if abs(times[j]-time)>1e-9: raise ValueError("Instante no muestreado")
        h=np.array([histogram(run[j],edges) for run in speeds])
        for a,b,y,s in zip(edges[:-1],edges[1:],h.mean(axis=0),h.std(axis=0,ddof=1)):
            snapshots.append(dict(time_s=time,v_left_m_s=float(a),v_right_m_s=float(b),
                                  density_mean=float(y),density_std=float(s)))
    save_csv(results/"speed-snapshots.csv",snapshots)
    summary=dict(n=c["n"],realizations=len(cases),mass_kg=mass,
        stationary_interval_s=[stationary_start,c["duration"]],end_exclusive=True,
        frames_per_run=int(mask.sum()),bin_edges_m_s=edges.tolist(),
        theta_fit_of_mean_J=theta,theta_fit_per_run_mean_J=float(np.mean([r["theta_fit_J"] for r in per_run])),
        theta_fit_per_run_std_J=float(np.std([r["theta_fit_J"] for r in per_run],ddof=1)),
        theta_initial_reference_J=reference,sse=sse,
        kinetic_per_particle_mean_J=float(np.mean([r["kinetic_per_particle_J"] for r in per_run])),
        kinetic_per_particle_std_J=float(np.std([r["kinetic_per_particle_J"] for r in per_run],ddof=1)),
        potential_per_particle_mean_J=float(np.mean([r["potential_per_particle_J"] for r in per_run])),
        relative_difference_from_initial=theta/reference-1,
        maximum_sampled_relative_energy_error=max(r["maximum_sampled_relative_energy_error"] for r in cases),
        bin_offset_m_s=first if first<width else 0,
        analysis="reanalisis de las muestras guardadas" if reanalyze else "simulacion y analisis",
        stationarity_policy=f"primer sufijo de ventanas de {c['window_s']:g} s, excluyendo la inicial, con al menos tres comparaciones: TV<=0.05 y cambio theta<=2%; diagnostico descriptivo",
        error_bars="desvio estandar entre diez realizaciones; no SEM ni incertidumbre del ajuste a la media")
    save_json(results/"speed-summary.json",summary)

    plt.rcParams.update({"font.size":11})
    fig,axes=plt.subplots(1,2,figsize=(12,4.6),layout="constrained")
    for time in [0,.1,.5,1]:
        rows=[r for r in snapshots if r["time_s"]==time]
        axes[0].stairs([r["density_mean"] for r in rows],edges,label=f"t = {time:g} s")
    for time in [5,30,60]:
        rows=[r for r in snapshots if r["time_s"]==time]
        axes[1].stairs([r["density_mean"] for r in rows],edges,label=f"t = {time:g} s")
    for ax in axes:
        ax.set(xlabel="Rapidez v [m/s]",ylabel="Densidad f(v) [s/m]",xlim=(0,edges[-1]))
        ax.legend(); ax.grid(alpha=.2)
    axes[0].set_title("Redistribución inicial")
    axes[1].set_title("Distribuciones tardías")
    fig.suptitle("N = 100 sin obstáculos · promedio de 10 realizaciones")
    fig.savefig(figures/"speed-evolution.png",dpi=180); plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(12,4.6),layout="constrained")
    axes[0].errorbar(centers,mean,yerr=sd,fmt="o",markersize=3,capsize=2,label="Media ± desvío entre realizaciones")
    v=np.linspace(0,edges[-1],500)
    axes[0].plot(v,mass*v/theta*np.exp(-mass*v*v/(2*theta)),label="Maxwell–Boltzmann ajustada")
    axes[0].set(xlabel="Rapidez v [m/s]",ylabel="Densidad f(v) [s/m]",
                title=f"Ventana estacionaria [{stationary_start:g}, {c['duration']:g}) s")
    axes[0].legend(fontsize=9)
    candidates=np.linspace(.95*reference,1.05*reference,251)
    errors=[np.sum((mean-mb_bins(edges,mass,t))**2) for t in candidates]
    save_csv(results/"speed-objective.csv",[dict(theta_J=float(t),sse=float(e)) for t,e in zip(candidates,errors)])
    axes[1].plot(candidates,errors)
    axes[1].axvline(theta,color="C1",label="Mínimo de cuadrados")
    axes[1].axvline(reference,color="gray",ls="--",label="Referencia inicial")
    axes[1].set(xlabel="Energía térmica kBT [J]",ylabel="Suma de errores cuadrados [(s/m)²]",
                title="Ajuste de un único parámetro")
    axes[1].ticklabel_format(axis="x",style="sci",scilimits=(0,0)); axes[1].legend(fontsize=9)
    for ax in axes: ax.grid(alpha=.2)
    fig.savefig(figures/"speed-fit.png",dpi=180); plt.close(fig)
    artifacts=[results/filename for filename in ["speed-contract.json","speed-summary.json","speed-windows.csv",
        "speed-fit-per-run.csv","speed-stationary.csv","speed-snapshots.csv","speed-objective.csv"]]
    artifacts += sorted(cases_dir.glob("*"))+[figures/"speed-fit.png",figures/"speed-evolution.png"]
    save_json(results/"speed-manifest.json",dict(fingerprint=fingerprint,
        artifacts={str(p.relative_to(ROOT)):digest(p) for p in artifacts}))
    print(json.dumps(summary,indent=2),flush=True)


if __name__=="__main__": main()
