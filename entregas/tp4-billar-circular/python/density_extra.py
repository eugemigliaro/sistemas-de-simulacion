"""Completa diez realizaciones N=50 tras el indicio del mapa a x0=r."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from billiard_analysis import frames,Energy,maximum_relative_error
from performance_analysis import conversion_times
from density_analysis import summarize_groups
from density_study import ROOT,RESULTS,RAW,digest,save_json,save_csv


def main():
    inputs=[RESULTS/f'density-position-cases/map-n50-x00-seed{s}.json' for s in range(1,6)]
    binary=ROOT/'cpp/build/release/tp4'
    sources=[Path(__file__),ROOT/'python/billiard_analysis.py',ROOT/'python/performance_analysis.py',
             ROOT/'python/density_analysis.py',ROOT/'python/density_study.py']
    contract=dict(inputs_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
        source_sha256={str(p.relative_to(ROOT)):digest(p) for p in sources},
        binary_sha256=digest(binary),n=50,new_seeds=[6,7,8,9,10],duration=300.,dt=.0000125,workers=2)
    fingerprint=hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
    contract_path=RESULTS/'density-extra-contract.json'
    if contract_path.exists() and json.loads(contract_path.read_text())['fingerprint']!=fingerprint:
        raise ValueError('N=50: fuentes incompatibles')
    save_json(contract_path,dict(fingerprint=fingerprint,**contract))
    folder=RESULTS/'density-extra-cases';folder.mkdir(exist_ok=True)
    reused=[json.loads(p.read_text()) for p in inputs]
    for a in reused:assert digest(ROOT/a['trajectory'])==a['trajectory_sha256']

    def run(seed):
        name=f'extra-n50-seed{seed}';checkpoint=folder/(name+'.json')
        if checkpoint.exists():
            a=json.loads(checkpoint.read_text());assert a['extra_fingerprint']==fingerprint
            assert digest(ROOT/a['trajectory'])==a['trajectory_sha256']
            assert digest(ROOT/a['energy_series'])==a['energy_series_sha256']
            return a
        path=RAW/(name+'.csv')
        cmd=[str(binary),'billiard','--n','50','--seed',str(seed),'--duration','300',
             '--dt','0.0000125','--save-every','80000','--obstacles','1','--obstacle-x','0.0175',
             '--output',str(path)]
        print(name+': simulando',flush=True)
        subprocess.run(cmd,check=True,capture_output=True,text=True)
        meta=json.loads(Path(str(path)+'.json').read_text());calc=Energy(meta);energy=[];final=None
        for step,time,state in frames(path,meta):
            final=state;components=calc.components(state)
            energy.append([step,time,*components,sum(components)])
        error=maximum_relative_error(np.asarray(energy))
        if error>.001:raise ValueError('N=50: error energetico excesivo')
        series=RESULTS/(name+'-energy.csv')
        np.savetxt(series,energy,delimiter=',',comments='',
                    header='step,time_s,kinetic_J,pair_J,wall_J,obstacle_J,total_J')
        a=dict(extra_fingerprint=fingerprint,n=50,obstacle_x=.0175,seed=seed,duration=300.,dt=meta['dt'],
            conversion=conversion_times(final,meta['dt'],300),first_contacts=final[:,8].astype(int).tolist(),
            trajectory=str(path.relative_to(ROOT)),trajectory_sha256=digest(path),metadata=meta,
            maximum_sampled_relative_energy_error=error,energy_series=str(series.relative_to(ROOT)),
            energy_series_sha256=digest(series),command=[str(Path(t).relative_to(ROOT)) if t.startswith(str(ROOT)) else t for t in cmd])
        save_json(checkpoint,a);print(name+': '+str(a['conversion']),flush=True)
        return a
    with ThreadPoolExecutor(max_workers=2) as pool:cases=reused+list(pool.map(run,range(6,11)))
    output=RESULTS/'density-extra-cases.json';save_json(output,cases)
    summary=RESULTS/'density-extra-summary.csv';save_csv(summary,summarize_groups(cases))
    files=[contract_path,output,summary,*folder.glob('*.json'),
           *[ROOT/a['energy_series'] for a in cases if 'extra_fingerprint' in a]]
    save_json(RESULTS/'density-extra-manifest.json',dict(fingerprint=fingerprint,
        artifacts={str(p.relative_to(ROOT)):digest(p) for p in files}))


if __name__=='__main__':main()
