"""Censura administrativa, medias completas y mínimos certificados en una grilla."""
import math
import numpy as np


def summarize_groups(cases):
    rows=[]
    for n,x in sorted({(c['n'],c['obstacle_x']) for c in cases}):
        group=[c for c in cases if (c['n'],c['obstacle_x'])==(n,x)]
        if len({c['seed'] for c in group})!=len(group):
            raise ValueError('Semillas repetidas en grupo')
        row=dict(n=n,density_m2=n/(math.pi*.51**2),obstacle_x_m=x,repetitions=len(group),
                 fu_final_mean=float(np.mean([c['conversion']['fu_final'] for c in group])))
        for key in ['t90','t100']:
            values=[c['conversion'][key+'_s'] for c in group]
            observed=[v for v in values if v is not None]
            if any(v is not None and (v<0 or v>c['duration']+1e-9) for v,c in zip(values,group)):
                raise ValueError('Tiempo fuera del seguimiento')
            complete=len(observed)==len(values)
            row[key+'_censored']=len(values)-len(observed)
            row[key+'_mean_s']=float(np.mean(observed)) if complete else None
            row[key+'_std_s']=float(np.std(observed,ddof=1)) if complete and len(observed)>1 else None
            row[key+'_mean_lower_bound_s']=float(np.mean([v if v is not None else c['duration']
                                                        for v,c in zip(values,group)]))
        rows.append(row)
    return rows


def best_positions(rows):
    """Solo certifica un mínimo muestral si ninguna cota censurada puede mejorarlo."""
    result=[]
    for n in sorted({r['n'] for r in rows}):
        group=[r for r in rows if r['n']==n]
        complete=[r for r in group if r['t90_mean_s'] is not None]
        if not complete:
            result.append(dict(n=n,position_m=None,certified_on_grid=False));continue
        best=min(complete,key=lambda r:r['t90_mean_s'])
        censored=[r for r in group if r['t90_mean_s'] is None]
        certified=all(r['t90_mean_lower_bound_s']>=best['t90_mean_s'] for r in censored)
        result.append(dict(n=n,position_m=best['obstacle_x_m'],mean_s=best['t90_mean_s'],
            std_s=best['t90_std_s'],certified_on_grid=certified,
            meaning='minimo de medias muestrales en grilla; no optimo poblacional exacto'))
    return result


def restricted_summary(cases,cutoff):
    """Media muestral de min(T,tau); no se presenta como media completa de T."""
    if cutoff<=0: raise ValueError('Corte no positivo')
    rows=[]
    for n in sorted({c['n'] for c in cases}):
        group=[c for c in cases if c['n']==n]
        row=dict(n=n,density_m2=n/(math.pi*.51**2),cutoff_s=cutoff,repetitions=len(group))
        for key in ['t90','t100']:
            values=[]
            for c in group:
                t=c['conversion'][key+'_s']
                if t is None and c['duration']<cutoff:
                    raise ValueError('Seguimiento insuficiente para media restringida')
                values.append(min(t,cutoff) if t is not None else cutoff)
            row[key+'_restricted_mean_s']=float(np.mean(values))
            row[key+'_restricted_std_s']=float(np.std(values,ddof=1)) if len(values)>1 else None
        rows.append(row)
    return rows
