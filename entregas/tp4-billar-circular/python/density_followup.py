"""Seguimiento selectivo a 600 s de grupos N<=400 censurados a 300 s."""
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
    source=RESULTS/'density-extended-cases.json'
    base=json.loads(source.read_text())
    binary=ROOT/'cpp/build/release/tp4'
    contract=dict(source_sha256=digest(source),script_sha256=digest(Path(__file__)),
        simulation_contract_sha256=digest(RESULTS/'density-position-contract.json'),
        binary_sha256=digest(binary),duration=600.,max_n=400)
    fingerprint=hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
    contract_path=RESULTS/'density-followup-contract.json'
    if contract_path.exists() and json.loads(contract_path.read_text())['fingerprint']!=fingerprint:
        raise ValueError('Seguimiento incompatible')
    save_json(contract_path,dict(fingerprint=fingerprint,**contract))
    folder=RESULTS/'density-followup-cases';folder.mkdir(exist_ok=True)

    def follow(a):
        if a['n']>400 or a['conversion']['t100_s'] is not None:return a
        name=f"follow-n{a['n']}-seed{a['seed']}"
        checkpoint=folder/(name+'.json')
        if checkpoint.exists():
            result=json.loads(checkpoint.read_text())
            assert result['followup_fingerprint']==fingerprint
            assert digest(ROOT/result['trajectory'])==result['trajectory_sha256']
            assert digest(ROOT/result['energy_series'])==result['energy_series_sha256']
            return result
        path=RAW/(name+'.csv');dt=a['dt']
        command=[str(binary),'billiard','--n',str(a['n']),'--seed',str(a['seed']),
            '--duration','600','--dt',str(dt),'--save-every',str(round(1/dt)),
            '--obstacles','1','--obstacle-x','0.0175','--initial',str(ROOT/a['initial']),
            '--output',str(path)]
        print(name+': extendiendo a 600 s',flush=True)
        subprocess.run(command,check=True,capture_output=True,text=True)
        meta=json.loads(Path(str(path)+'.json').read_text())
        energy=[];calculator=Energy(meta);state300=None;final=None
        for step,time,state in frames(path,meta):
            if time==300:state300=state.copy()
            final=state
            components=calculator.components(state)
            energy.append([step,time,*components,sum(components)])
        old_final=list(frames(ROOT/a['trajectory'],a['metadata']))[-1][2]
        np.testing.assert_array_equal(old_final,state300)
        error=maximum_relative_error(np.asarray(energy))
        if error>.001:raise ValueError(name+': error energetico excesivo')
        series=RESULTS/(name+'-energy.csv')
        np.savetxt(series,energy,delimiter=',',comments='',
            header='step,time_s,kinetic_J,pair_J,wall_J,obstacle_J,total_J')
        result=dict(a,duration=600.,metadata=meta,followup_fingerprint=fingerprint,
            previous_trajectory=a['trajectory'],previous_trajectory_sha256=a['trajectory_sha256'],
            trajectory=str(path.relative_to(ROOT)),trajectory_sha256=digest(path),
            energy_series=str(series.relative_to(ROOT)),energy_series_sha256=digest(series),
            maximum_sampled_relative_energy_error=error,
            first_contacts=final[:,8].astype(int).tolist(),conversion=conversion_times(final,dt,600),
            command=[str(Path(t).relative_to(ROOT)) if t.startswith(str(ROOT)) else t for t in command],
            prefix300_exactly_verified=True)
        save_json(checkpoint,result)
        print(name+': '+str(result['conversion']),flush=True)
        return result

    with ThreadPoolExecutor(max_workers=4) as pool:cases=list(pool.map(follow,base))
    output=RESULTS/'density-final-cases.json';save_json(output,cases)
    summary=RESULTS/'density-final-summary.csv';save_csv(summary,summarize_groups(cases))
    files=[contract_path,output,summary,*folder.glob('*.json'),
        *[ROOT/a['energy_series'] for a in cases if 'followup_fingerprint' in a]]
    save_json(RESULTS/'density-followup-manifest.json',dict(fingerprint=fingerprint,
        artifacts={str(p.relative_to(ROOT)):digest(p) for p in files}))
    print('Seguimiento selectivo finalizado',flush=True)


if __name__=='__main__':main()
