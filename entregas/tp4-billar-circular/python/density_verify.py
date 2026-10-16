"""Auditoría independiente de integridad, cobertura y estadísticas del punto 2.4."""
import json
from pathlib import Path
import numpy as np
from density_study import digest,save_json
from density_analysis import summarize_groups,best_positions,restricted_summary
from performance_analysis import conversion_times

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'experiments/results'


def main():
    contract=json.loads((RESULTS/'density-position-contract.json').read_text())
    c=contract['config']
    for field in ['source_sha256','input_sha256']:
        for name,expected in contract[field].items():
            assert digest(ROOT/name)==expected,(field,name)
    assert digest(ROOT/'cpp/build/release/tp4')==contract['binary_sha256']
    for filename in ['density-position-manifest.json','density-followup-manifest.json','density-extra-manifest.json',
                     'density-plot-manifest.json']:
        m=json.loads((RESULTS/filename).read_text())
        for field in ['artifacts','source_sha256']:
            for name,expected in m.get(field,{}).items():assert digest(ROOT/name)==expected,name
    base=json.loads((RESULTS/'density-baseline-cases.json').read_text())
    extended=json.loads((RESULTS/'density-extended-cases.json').read_text())
    final=json.loads((RESULTS/'density-final-cases.json').read_text())
    complete=json.loads((RESULTS/'density-complete-cases.json').read_text())
    extra_contract=json.loads((RESULTS/'density-extra-contract.json').read_text())
    for field in ['source_sha256','inputs_sha256']:
        for name,expected in extra_contract[field].items():assert digest(ROOT/name)==expected
    followup_contract=json.loads((RESULTS/'density-followup-contract.json').read_text())
    assert digest(ROOT/'python/density_followup.py')==followup_contract['script_sha256']
    heatmap=json.loads((RESULTS/'density-heatmap-cases.json').read_text())
    assert len(base)==len(extended)==len(final)==len(c['density_counts'])*len(c['density_seeds'])
    assert len(complete)==60
    expected={(n,x,s) for n in c['heatmap_counts'] for x in c['positions_m'] for s in c['heatmap_seeds']}
    assert len(heatmap)==len(expected)
    assert {(a['n'],a['obstacle_x'],a['seed']) for a in heatmap}==expected
    generated=list((RESULTS/'density-position-cases').glob('*.json'))
    generated+=list((RESULTS/'density-followup-cases').glob('*.json'))
    generated+=list((RESULTS/'density-extra-cases').glob('*.json'))
    maxima=[]
    for path in generated:
        a=json.loads(path.read_text())
        if 'extra_fingerprint' in a:assert a['extra_fingerprint']==extra_contract['fingerprint']
        else:assert a['fingerprint']==contract['fingerprint']
        if 'followup_fingerprint' in a:
            assert a['followup_fingerprint']==followup_contract['fingerprint']
            assert a['prefix300_exactly_verified']
        assert digest(ROOT/a['trajectory'])==a['trajectory_sha256']
        if a.get('initial'):assert digest(ROOT/a['initial'])==a['initial_sha256']
        for attempt in a.get('attempts',[]):
            assert digest(ROOT/attempt['trajectory'])==attempt['trajectory_sha256']
            assert digest(ROOT/attempt['energy_series'])==attempt['energy_series_sha256']
        series=np.loadtxt(ROOT/a['energy_series'],delimiter=',',skiprows=1)
        error=float(np.max(np.abs(series[:,-1]/series[0,-1]-1)))
        assert abs(error-a['maximum_sampled_relative_energy_error'])<1e-14
        assert error<=c['relative_energy_tolerance']
        maxima.append(error)
    for collection in [base,extended,final,complete,heatmap]:
        for a in collection:
            contacts=np.array(a['first_contacts'])
            assert contacts.shape==(a['n'],)
            assert np.all(contacts>=-1)
            assert np.all(contacts[contacts>=0]*a['dt']<=a['duration']+1e-9)
            state=np.zeros((a['n'],9));state[:,8]=contacts
            assert conversion_times(state,a['dt'],a['duration'])==a['conversion']
            v=a['conversion'];assert v['t100_s'] is None or v['t90_s']<=v['t100_s']
            if collection is heatmap:assert a['duration']==c['heatmap_duration']
        # Independientemente de la función de agrupado, recomputar las medias/SD.
        for r in summarize_groups(collection):
            group=[a for a in collection if (a['n'],a['obstacle_x'])==(r['n'],r['obstacle_x_m'])]
            for key in ['t90','t100']:
                values=[a['conversion'][key+'_s'] for a in group]
                assert r[key+'_censored']==sum(t is None for t in values)
                if all(t is not None for t in values):
                    assert abs(r[key+'_mean_s']-np.mean(values))<1e-12
                    assert abs(r[key+'_std_s']-np.std(values,ddof=1))<1e-12
                else:assert r[key+'_mean_s'] is None and r[key+'_std_s'] is None
    best=best_positions(summarize_groups(heatmap))
    assert best==json.loads((RESULTS/'density-best-positions.json').read_text())
    restricted_summary(base,30);restricted_summary(extended,c['density_extension_duration'])
    for b in json.loads((RESULTS/'density-best-tested.json').read_text()):
        rows=summarize_groups(complete);key=b['observable']
        observed_rows=[r for r in rows if r[key+'_mean_s'] is not None]
        assert b['mean_s']==min(r[key+'_mean_s'] for r in observed_rows)
    save_json(RESULTS/'density-verification.json',dict(status='passed',
        contract_fingerprint=contract['fingerprint'],generated_cases=len(generated),
        baseline_cases=len(base),extended_cases=len(extended),final_density_cases=len(complete),heatmap_cases=len(heatmap),
        maximum_sampled_relative_energy_error=max(maxima),
        verified=['source/input/binary/artifact hashes','complete grid and unique seeds',
            'all generated trajectories and energy series','contact horizons including truncation',
            'conversion times, censures, means and sample SD','restricted means and minima on grid'],
        verifier_sha256=digest(Path(__file__))))
    print('Auditoria del punto 2.4: OK')


if __name__=='__main__':main()
