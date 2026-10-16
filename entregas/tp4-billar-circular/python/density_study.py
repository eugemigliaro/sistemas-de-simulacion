"""TP4 2.4: seguimiento complementario y barrido (x0,N), con fuentes intactas."""
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
from billiard_analysis import frames, Energy, maximum_relative_error
from performance_analysis import conversion_times
from density_analysis import summarize_groups,best_positions,restricted_summary

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'experiments/results'
RAW=ROOT/'experiments/raw/density-position'
CASES=RESULTS/'density-position-cases'


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def save_json(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def save_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def conversion(contacts,dt,duration):
    state=np.zeros((len(contacts),9));state[:,8]=contacts
    return conversion_times(state,dt,duration)


def main():
    c=json.loads((ROOT/'experiments/configs/density-position.json').read_text())
    binary=ROOT/'cpp/build/release/tp4'
    for p in [RAW,CASES]:p.mkdir(parents=True,exist_ok=True)
    baseline_paths=[RESULTS/f'performance-cases/tp4-n{n}-seed{s}.json'
                    for n in c['density_counts'] for s in c['density_seeds']]
    position_paths=sorted((RESULTS/'position-cases').glob('*.json'))
    sources=[ROOT/'cpp/src/main.cpp',*sorted((ROOT/'cpp/include').rglob('*.hpp')),
        Path(__file__),ROOT/'python/density_analysis.py',ROOT/'python/billiard_analysis.py',
        ROOT/'python/performance_analysis.py']
    contract=dict(config=c,binary_sha256=digest(binary),
        source_sha256={str(p.relative_to(ROOT)):digest(p) for p in sources},
        input_sha256={str(p.relative_to(ROOT)):digest(p) for p in baseline_paths+position_paths},
        python=sys.version,numpy=np.__version__,platform=platform.platform())
    fingerprint=hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
    contract_path=RESULTS/'density-position-contract.json'
    if contract_path.exists() and json.loads(contract_path.read_text())['fingerprint']!=fingerprint:
        raise ValueError('Fuentes/configuracion cambiaron: no mezclar checkpoints')
    save_json(contract_path,dict(fingerprint=fingerprint,**contract))
    baseline=[json.loads(p.read_text()) for p in baseline_paths]
    positions=[(p,json.loads(p.read_text())) for p in position_paths]

    def verify_trajectory(case):
        path=ROOT/case['trajectory']
        if digest(path)!=case['trajectory_sha256']:raise ValueError('Trayectoria fuente alterada')
        return path

    # Salidas obligatorias de 30 s: se conservan como conjunto independiente.
    base=[];initial_paths={}
    for old in baseline:
        path=verify_trajectory(old)
        snapshots=list(frames(path,old['metadata']))
        initial=snapshots[0][2]
        initial_path=RAW/f"initial-n{old['n']}-seed{old['seed']}.csv"
        with initial_path.open('w') as f:
            f.write('id,x,y,vx,vy\n')
            for row in initial:f.write(str(int(row[2]))+','+','.join(format(x,'.17g') for x in row[3:7])+'\n')
        initial_paths[old['n'],old['seed']]=initial_path
        base.append(dict(n=old['n'],seed=old['seed'],obstacle_x=.0175,duration=30.,
            conversion=conversion_times(snapshots[-1][2],old['metadata']['dt'],30),
            first_contacts=snapshots[-1][2][:,8].astype(int).tolist(),dt=old['metadata']['dt'],
            source=old['trajectory']))

    def simulate(name,n,x,seed,duration,initial=None):
        checkpoint=CASES/(name+'.json')
        if checkpoint.exists():
            result=json.loads(checkpoint.read_text())
            if result['fingerprint']!=fingerprint:raise ValueError('Checkpoint incompatible')
            verify_trajectory(result)
            if digest(ROOT/result['energy_series'])!=result['energy_series_sha256']:
                raise ValueError('Serie energetica alterada')
            return result
        attempts=[]
        for refinement in range(c['max_refinements']+1):
            dt=c['start_dt']/2**refinement
            path=RAW/f'{name}-h{refinement}.csv'
            command=[str(binary),'billiard','--n',str(n),'--seed',str(seed),
                '--duration',str(duration),'--dt',str(dt),'--save-every',str(round(c['save_interval']/dt)),
                '--obstacles','1','--obstacle-x',str(x),'--output',str(path)]
            if initial:command+=['--initial',str(initial)]
            print(f'{name}: simulando h={dt:g}, tf={duration:g}',flush=True)
            process=subprocess.run(command,capture_output=True,text=True)
            if process.returncode:raise RuntimeError(name+': '+process.stderr)
            meta=json.loads(Path(str(path)+'.json').read_text())
            energy=[];calculator=Energy(meta);first=None;final=None
            for step,time,state in frames(path,meta):
                if first is None:first=state.copy()
                final=state
                components=calculator.components(state)
                energy.append([step,time,*components,sum(components)])
            series=np.asarray(energy);error=maximum_relative_error(series)
            series_path=RESULTS/f'{name}-h{refinement}-energy.csv'
            np.savetxt(series_path,series,delimiter=',',comments='',
                header='step,time_s,kinetic_J,pair_J,wall_J,obstacle_J,total_J')
            attempts.append(dict(dt=dt,trajectory=str(path.relative_to(ROOT)),trajectory_sha256=digest(path),
                maximum_sampled_relative_energy_error=error,energy_series=str(series_path.relative_to(ROOT)),
                energy_series_sha256=digest(series_path)))
            if error<=c['relative_energy_tolerance']:break
            print(f'{name}: error={error:g}, refinando sin borrar ensayo',flush=True)
        else:raise ValueError(name+': control energetico no satisfecho')
        if initial:
            imported=np.loadtxt(initial,delimiter=',',skiprows=1)
            np.testing.assert_array_equal(first[:,3:7],imported[:,1:5])
        result=dict(fingerprint=fingerprint,n=n,obstacle_x=x,seed=seed,duration=duration,
            conversion=conversion_times(final,dt,duration),first_contacts=final[:,8].astype(int).tolist(),
            metadata=meta,attempts=attempts,**attempts[-1],
            command=[str(Path(a).relative_to(ROOT)) if a.startswith(str(ROOT)) else a for a in command],
            initial=str(initial.relative_to(ROOT)) if initial else None,
            initial_sha256=digest(initial) if initial else None)
        # dt está registrado tanto en el caso como en el último intento.
        save_json(checkpoint,result)
        print(f"{name}: {result['conversion']}, error E={error:.3g}",flush=True)
        return result

    # Las corridas de 100 s ya completas aportan tiempos exactos: no requieren
    # integrarse hasta 300 s para conocer un primer cruce que ya ocurrió.
    density=[];pending=[]
    for old in baseline:
        n,seed=old['n'],old['seed']
        candidates=[(p,a) for p,a in positions if a['n']==n and a['seed']==seed and
                    a['obstacle_x']==.0175 and a['conversion']['t100_s'] is not None]
        if candidates:
            p,a=candidates[0];path=verify_trajectory(a)
            initial_state=next(frames(path,a['metadata']))[2]
            imported=np.loadtxt(initial_paths[n,seed],delimiter=',',skiprows=1)
            np.testing.assert_array_equal(initial_state[:,3:7],imported[:,1:5])
            density.append(dict(a,reused_from=str(p.relative_to(ROOT))))
        else:pending.append((f'long-n{n}-seed{seed}',n,.0175,seed,c['density_extension_duration'],initial_paths[n,seed]))
    with ThreadPoolExecutor(max_workers=c['workers']) as pool:
        futures=[pool.submit(simulate,*task) for task in sorted(pending,key=lambda t:-t[1])]
        for future in as_completed(futures):density.append(future.result())
    density.sort(key=lambda a:(a['n'],a['seed']))
    save_json(RESULTS/'density-extended-cases.json',density)
    save_json(RESULTS/'density-baseline-cases.json',base)

    heatmap=[];pending=[]
    for n in c['heatmap_counts']:
        for index,x in enumerate(c['positions_m']):
            for seed in c['heatmap_seeds']:
                candidates=[(p,a) for p,a in positions if (a['n'],a['obstacle_x'],a['seed'])==(n,x,seed)]
                if candidates:
                    p,a=candidates[0];verify_trajectory(a)
                    heatmap.append(dict(a,reused_from=str(p.relative_to(ROOT))))
                elif x==.0175 and n in c['density_counts']:
                    # Truncar explícitamente la historia de contactos al corte de 100 s.
                    a=next(a for a in density if (a['n'],a['seed'])==(n,seed))
                    contacts=np.array(a['first_contacts'])
                    contacts[contacts*a['dt']>c['heatmap_duration']]=-1
                    heatmap.append(dict(a,duration=c['heatmap_duration'],first_contacts=contacts.tolist(),
                        conversion=conversion(contacts,a['dt'],c['heatmap_duration']),
                        reused_from='density-extended-cases.json; contactos truncados a 100 s'))
                else:pending.append((f'map-n{n}-x{index:02d}-seed{seed}',n,x,seed,c['heatmap_duration']))
    with ThreadPoolExecutor(max_workers=c['workers']) as pool:
        futures=[pool.submit(simulate,*task) for task in sorted(pending,key=lambda t:-t[1])]
        for future in as_completed(futures):heatmap.append(future.result())
    heatmap.sort(key=lambda a:(a['n'],a['obstacle_x'],a['seed']))
    save_json(RESULTS/'density-heatmap-cases.json',heatmap)
    save_csv(RESULTS/'density-baseline-summary.csv',summarize_groups(base))
    save_csv(RESULTS/'density-extended-summary.csv',summarize_groups(density))
    save_csv(RESULTS/'density-restricted-30.csv',restricted_summary(base,30))
    save_csv(RESULTS/'density-restricted-300.csv',restricted_summary(density,c['density_extension_duration']))
    map_rows=summarize_groups(heatmap)
    save_csv(RESULTS/'density-heatmap-summary.csv',map_rows)
    save_json(RESULTS/'density-best-positions.json',best_positions(map_rows))
    save_csv(RESULTS/'density-position-raw.csv',[dict(study=label,n=a['n'],x0_m=a['obstacle_x'],seed=a['seed'],
        dt=a['dt'],duration_s=a['duration'],**a['conversion'])
        for label,collection in [('baseline',base),('extended',density),('heatmap',heatmap)] for a in collection])
    artifacts=[contract_path,*sorted(RESULTS.glob('density-*-cases.json')),
        *[RESULTS/name for name in ['density-baseline-summary.csv','density-extended-summary.csv',
          'density-restricted-30.csv','density-restricted-300.csv','density-heatmap-summary.csv',
          'density-best-positions.json','density-position-raw.csv']],*sorted(CASES.glob('*.json')),
        *[ROOT/a['energy_series'] for a in density+heatmap if 'energy_series' in a]]
    save_json(RESULTS/'density-position-manifest.json',dict(fingerprint=fingerprint,
        artifacts={str(p.relative_to(ROOT)):digest(p) for p in artifacts}))
    print('Densidad y mapa completos:',len(density),len(heatmap),'realizaciones',flush=True)


if __name__=='__main__':main()
