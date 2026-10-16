"""Figuras independientes de TP4 2.4; no modifica contratos de simulación."""
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from density_study import save_json,save_csv,digest
from density_analysis import summarize_groups,best_positions
from position_analysis import used_fraction
from billiard_analysis import frames

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'experiments/results'
FIGURES=ROOT/'experiments/figures'
os.environ.setdefault('MPLBACKEND','Agg')
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'python/.matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'python/.cache'))
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def main():
    manifest=json.loads((RESULTS/'density-position-manifest.json').read_text())
    for name,expected in manifest['artifacts'].items():
        if digest(ROOT/name)!=expected:raise ValueError('Artefacto alterado: '+name)
    base=json.loads((RESULTS/'density-baseline-cases.json').read_text())
    final_path=RESULTS/'density-final-cases.json'
    if not final_path.exists():raise ValueError('Ejecutar density_followup.py primero')
    followup_manifest=RESULTS/'density-followup-manifest.json'
    for name,expected in json.loads(followup_manifest.read_text())['artifacts'].items():
        if digest(ROOT/name)!=expected:raise ValueError('Seguimiento alterado: '+name)
    extended=json.loads(final_path.read_text())
    extra_manifest=RESULTS/'density-extra-manifest.json'
    for name,expected in json.loads(extra_manifest.read_text())['artifacts'].items():
        if digest(ROOT/name)!=expected:raise ValueError('N=50 alterado: '+name)
    extended+=json.loads((RESULTS/'density-extra-cases.json').read_text())
    save_json(RESULTS/'density-complete-cases.json',extended)
    save_csv(RESULTS/'density-complete-summary.csv',summarize_groups(extended))
    density_counts=sorted({a['n'] for a in extended})
    heatmap=json.loads((RESULTS/'density-heatmap-cases.json').read_text())
    c=json.loads((ROOT/'experiments/configs/density-position.json').read_text())
    FIGURES.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':11})
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained',sharex=True)
    for row,cases,title in [(0,base,'Salidas obligatorias · corte 30 s'),
                             (1,extended,'Complemento + N=50 · cortes 300/600 s')]:
        summary=summarize_groups(cases)
        for col,key in enumerate(['t90','t100']):
            ax=axes[row,col]
            measured=[r for r in summary if r[key+'_mean_s'] is not None]
            censored=[r for r in summary if r[key+'_mean_s'] is None]
            if measured:
                original=[r for r in measured if r['n']!=50]
                ax.errorbar([r['density_m2'] for r in original],[r[key+'_mean_s'] for r in original],
                    yerr=[r[key+'_std_s'] for r in original],fmt='o',capsize=4,color='C0',
                    label='Media completa ± desvío')
                if row==1:
                    added=next(r for r in measured if r['n']==50)
                    ax.errorbar([added['density_m2']],[added[key+'_mean_s']],yerr=[added[key+'_std_s']],
                        fmt='D',capsize=4,color='C2',label='N=50 adicional · media ± desvío')
            if censored:
                ax.scatter([r['density_m2'] for r in censored],[r[key+'_mean_lower_bound_s'] for r in censored],
                    marker='^',s=65,facecolors='none',edgecolors='C1',label='Cota inferior de la media')
                for r in censored:
                    ax.annotate(f"{r[key+'_censored']}/{r['repetitions']} cens.",
                        (r['density_m2'],r[key+'_mean_lower_bound_s']),xytext=(0,9),
                        textcoords='offset points',ha='center',fontsize=8)
            ax.set(title=title,xlabel='Densidad N/(πR²) [m⁻²]',
                   ylabel=('t₉₀' if key=='t90' else 't₁₀₀')+' [s]')
            if row==1:ax.set_yscale('log')
            ax.margins(x=.09,y=.3);ax.grid(alpha=.2);ax.legend(fontsize=8,loc='lower right')
    fig.savefig(FIGURES/'density-final-times.png',dpi=180);plt.close(fig)

    grid=np.arange(round(c['density_extension_duration']/.5)+1)*.5
    fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
    fu_rows=[]
    for n in density_counts:
        group=[a for a in extended if a['n']==n]
        values=np.array([used_fraction(a['first_contacts'],a['dt'],grid) for a in group])
        mean,sd=values.mean(axis=0),values.std(axis=0,ddof=1)
        ax.plot(grid,mean,label=f'N={n}')
        ax.fill_between(grid,np.maximum(0,mean-sd),np.minimum(1,mean+sd),alpha=.12)
        fu_rows += [dict(n=n,time_s=float(t),fu_mean=float(y),fu_std=float(s)) for t,y,s in zip(grid,mean,sd)]
    ax.axhline(.9,color='black',ls='--',alpha=.4)
    ax.set(xlabel='Tiempo [s]',ylabel='Fracción usada Fᵤ(t)',ylim=(0,1.02),
           title='Primeros 300 s · 10 realizaciones · bandas: desvío estándar')
    ax.legend();ax.grid(alpha=.2)
    fig.savefig(FIGURES/'density-final-fu.png',dpi=180);plt.close(fig)
    save_csv(RESULTS/'density-final-fu.csv',fu_rows)

    # Desplazamiento a un mismo tiempo para apoyar la discusión de movilidad.
    # Dominio acotado y sin periodicidad: esto no estima una constante difusiva.
    mobility=[]
    for a in extended:
        initial=None;target=None
        for _,time,state in frames(ROOT/a['trajectory'],a['metadata']):
            if initial is None:initial=state[:,3:5].copy()
            if abs(time-100)<1e-9:
                target=state[:,3:5].copy();break
        if target is None:raise ValueError('Falta estado a 100 s para movilidad')
        mobility.append(dict(n=a['n'],seed=a['seed'],time_s=100.,
            mean_square_displacement_m2=float(np.mean(np.sum((target-initial)**2,axis=1))),
            radial_mean_square_displacement_m2=float(np.mean((np.linalg.norm(target,axis=1)-
                                                              np.linalg.norm(initial,axis=1))**2))))
    save_csv(RESULTS/'density-mobility-100-raw.csv',mobility)
    save_csv(RESULTS/'density-mobility-100.csv',[dict(n=n,time_s=100.,repetitions=len(values),
        mean_square_displacement_mean_m2=float(np.mean(values)),
        mean_square_displacement_std_m2=float(np.std(values,ddof=1)),
        radial_mean_square_displacement_mean_m2=float(np.mean(radial)),
        radial_mean_square_displacement_std_m2=float(np.std(radial,ddof=1)))
        for n in density_counts
        for values in [[r['mean_square_displacement_m2'] for r in mobility if r['n']==n]]
        for radial in [[r['radial_mean_square_displacement_m2'] for r in mobility if r['n']==n]]])

    rows=summarize_groups(heatmap);best=best_positions(rows)
    density_best=[]
    extended_summary=summarize_groups(extended)
    for key in ['t90','t100']:
        complete=[r for r in extended_summary if r[key+'_mean_s'] is not None]
        if not complete:continue
        b=min(complete,key=lambda r:r[key+'_mean_s'])
        other_censored=[r for r in extended_summary if r[key+'_mean_s'] is None]
        density_best.append(dict(observable=key,n=b['n'],density_m2=b['density_m2'],
            mean_s=b[key+'_mean_s'],std_s=b[key+'_std_s'],
            smallest_sample_mean_on_tested_grid=all(r[key+'_mean_lower_bound_s']>=b[key+'_mean_s']
                                                  for r in other_censored),
            at_boundary=b['n'] in [min(c['density_counts']),max(c['density_counts'])],
            meaning='comparacion muestral en N estudiados; sin prueba de optimo global o significancia'))
    save_json(RESULTS/'density-best-tested.json',density_best)
    counts=c['heatmap_counts'];positions=np.array(c['positions_m'])
    matrix=np.full((len(counts),len(positions)),np.nan)
    for i,n in enumerate(counts):
        for j,x in enumerate(positions):
            r=next(r for r in rows if r['n']==n and r['obstacle_x_m']==x)
            if r['t90_mean_s'] is not None:matrix[i,j]=r['t90_mean_s']
    dx=positions[1]-positions[0]
    boundaries=np.r_[positions-dx/2,positions[-1]+dx/2]
    fig,ax=plt.subplots(figsize=(12,5),layout='constrained')
    cmap=matplotlib.colormaps['viridis'].copy();cmap.set_bad('#dddddd')
    image=ax.pcolormesh(boundaries,np.arange(len(counts)+1),np.ma.masked_invalid(matrix),cmap=cmap)
    for i,n in enumerate(counts):
        for j,x in enumerate(positions):
            r=next(r for r in rows if r['n']==n and r['obstacle_x_m']==x)
            if np.isfinite(matrix[i,j]):
                text=f'{matrix[i,j]:.1f}'
                normalized=image.norm(matrix[i,j])
                color='white' if normalized<.5 else 'black'
            else:text=f"{r['t90_censored']}/5\ncens.";color='black'
            ax.text(x,i+.5,text,ha='center',va='center',fontsize=9,color=color)
        b=next(b for b in best if b['n']==n)
        if b['certified_on_grid']:
            ax.add_patch(plt.Rectangle((b['position_m']-dx/2,i),dx,1,fill=False,
                                     edgecolor='red',linewidth=2.5))
    ax.set(yticks=np.arange(len(counts))+.5,yticklabels=[str(n) for n in counts],
           xticks=positions,xlabel='Posición simétrica x₀ [m]',ylabel='N (densidades discretas)',
           title='Media de t₉₀ [s] · 5 realizaciones por celda · corte 100 s')
    ax.tick_params(axis='x',rotation=35)
    fig.colorbar(image,ax=ax,label='Media completa de t₉₀ [s]')
    ax.legend(handles=[Line2D([],[],color='red',linewidth=2.5,label='Menor media muestral por fila')],
              loc='upper center',bbox_to_anchor=(.5,-.23),frameon=False)
    fig.savefig(FIGURES/'density-position-heatmap.png',dpi=180);plt.close(fig)

    fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
    for n in counts:
        group=[r for r in rows if r['n']==n and r['t90_mean_s'] is not None]
        ax.errorbar([r['obstacle_x_m'] for r in group],[r['t90_mean_s'] for r in group],
            yerr=[r['t90_std_s'] for r in group],fmt='o-',capsize=3,label=f'N={n}')
        missing=[r for r in rows if r['n']==n and r['t90_mean_s'] is None]
        if missing:ax.scatter([r['obstacle_x_m'] for r in missing],
            [r['t90_mean_lower_bound_s'] for r in missing],marker='^',facecolors='none',edgecolors='black')
    ax.set(xlabel='Posición simétrica x₀ [m]',ylabel='t₉₀ [s]',
           title='Cortes del mapa · media ± desvío entre 5 realizaciones')
    ax.legend();ax.grid(alpha=.2)
    fig.savefig(FIGURES/'density-position-cuts.png',dpi=180);plt.close(fig)
    files=[FIGURES/name for name in ['density-final-times.png','density-final-fu.png',
        'density-position-heatmap.png','density-position-cuts.png']]+[RESULTS/name for name in
        ['density-final-fu.csv','density-mobility-100.csv','density-mobility-100-raw.csv','density-best-tested.json',
         'density-complete-cases.json','density-complete-summary.csv']]
    save_json(RESULTS/'density-plot-manifest.json',dict(simulation_fingerprint=manifest['fingerprint'],
        simulation_manifest_sha256=digest(RESULTS/'density-position-manifest.json'),
        followup_manifest_sha256=digest(followup_manifest),
        extra_manifest_sha256=digest(extra_manifest),
        source_sha256={str(p.relative_to(ROOT)):digest(p) for p in
            [Path(__file__),ROOT/'python/position_analysis.py',ROOT/'python/billiard_analysis.py']},
        matplotlib=matplotlib.__version__,artifacts={str(p.relative_to(ROOT)):digest(p) for p in files}))
    print(json.dumps(best,indent=2))


if __name__=='__main__':main()
