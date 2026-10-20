"""Figuras para exposición: fuentes verificadas, sin títulos ni captions internos."""
import csv
import hashlib
import json
import os
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'presentacion/figuras'
RESULTS=ROOT/'experiments/results'
os.environ.setdefault('MPLBACKEND','Agg')
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'python/.matplotlib'))
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FixedLocator, FuncFormatter, NullFormatter
from matplotlib.patches import Rectangle

SOURCES=set()
COLORS=['#005b91','#d35c20','#009e73','#7a5195','#b22222','#666666']


def table(name):
    p=RESULTS/name;SOURCES.add(p)
    with p.open() as f:return list(csv.DictReader(f))


def load(name):
    p=RESULTS/name;SOURCES.add(p)
    return np.genfromtxt(p,delimiter=',',names=True)


def setup(w=7,h=4.3):
    fig,ax=plt.subplots(figsize=(w,h),layout='constrained')
    ax.grid(alpha=.2);return fig,ax


def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'));fig.savefig(OUT/(name+'.png'),dpi=180);plt.close(fig)


def power_ten(value,_):
    """Rótulo a×10^b de un eje logarítmico, con la notación pedida en la guía."""
    exponent=int(np.floor(np.log10(value)+1e-9));mantissa=value/10**exponent
    return f'$10^{{{exponent}}}$' if abs(mantissa-1)<1e-9 else f'${mantissa:g}\\times10^{{{exponent}}}$'


def comma(value,digits):
    return f'{value:.{digits}f}'.replace('.','{,}')


def factor(value):
    return comma(value,1) if value<10 else f'{value:.0f}'


def performance_text(rows):
    """Texto de la D16 calculado desde el resumen, para no desactualizarlo al volver a medir."""
    mean={(r['engine'],int(r['n'])):float(r['runtime_mean_s']) for r in rows}
    lines=[r'\textbf{Al duplicar $N$}\\($100\to200\to400$)']
    for engine,label in [('tp4','TP4'),('tp3','TP3')]:
        a,b=mean[(engine,200)]/mean[(engine,100)],mean[(engine,400)]/mean[(engine,200)]
        lines.append(f'{label}: $\\times{factor(a)}$ y $\\times{factor(b)}$')
    if ('tp3',650) in mean and ('tp4',650) in mean:
        lines.append(f'$N=650$: TP3 es $\\times{factor(mean[("tp3",650)]/mean[("tp4",650)])}$ más lento')
    contract=RESULTS/'performance-contract-v2.json'
    if not contract.exists():contract=RESULTS/'performance-contract.json'
    SOURCES.add(contract)
    cpu=json.loads(contract.read_text())['cpu']
    return (r'\newcommand{\rendimientoCPU}{'+cpu+'}\n'
            r'\newcommand{\rendimientoTexto}{'+'\\\\'.join(lines)+'}\n')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':18,'axes.labelsize':20,'legend.fontsize':16,
                         'axes.prop_cycle':plt.cycler(color=COLORS),'axes.spines.top':False,'axes.spines.right':False})
    # Una sola figura de ECM frente al paso. Beeman, Verlet y Velocity Verlet tienen el mismo
    # orden y se superponen en log-log; la franja inferior muestra su cociente con Verlet original.
    fig,(ax,rel)=plt.subplots(2,1,figsize=(10,4.7),sharex=True,height_ratios=[2.3,1],layout='constrained')
    rows=table('oscillator-summary.csv')
    def ecm(method):
        g=sorted([r for r in rows if r['method']==method],key=lambda r:float(r['dt_s']))
        return np.array([float(r['dt_s']) for r in g]),np.array([float(r['ecm_m2']) for r in g])
    methods=[('beeman','Beeman','o',{}),
             ('verlet','Verlet original','s',dict(markerfacecolor='none',markeredgewidth=1.8,markersize=10)),
             ('velocity-verlet','Velocity Verlet','x',dict(markeredgewidth=2.2,markersize=9)),
             ('euler-pc','Euler predictor-corrector','^',{})]
    for (method,label,marker,style),color in zip(methods,COLORS):
        dt,e=ecm(method)
        ax.loglog(dt,e,marker=marker,label=label,linewidth=1.6,color=color,**{'markersize':8,**style})
    ax.set(ylabel='ECM (m²)',yticks=[1e-14,1e-11,1e-8,1e-5,1e-2]);ax.grid(alpha=.2)
    ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),frameon=False)
    dt,ref=ecm('verlet')
    for (method,label,marker,style),color in list(zip(methods,COLORS))[:3]:
        rel.semilogx(dt,ecm(method)[1]/ref,marker=marker,linewidth=1.6,color=color,**{'markersize':8,**style})
    rel.set(xlabel='Paso de integración (s)',ylim=(.82,1.04),yticks=[.85,1]);rel.grid(alpha=.2)
    rel.set_ylabel('ECM relativo\na Verlet',fontsize=16)
    save(fig,'oscilador-ecm')

    fig,ax=setup()
    for value,label in [('0.0005',r'$5\times10^{-4}$'),('0.0001',r'$10^{-4}$'),('5e-05',r'$5\times10^{-5}$')]:
        a=load('energy-dt-'+value+'.csv')
        initial = a['total_J'][0]
        ax.plot(a['time_s'],100*(a['total_J']/initial-1),label=label+' s',linewidth=1.2)
    ax.set(xlabel='Tiempo (s)',ylabel='Variación de energía (%)');ax.legend();save(fig,'energia-tiempo')
    fig,ax=setup();a=load('energy-summary.csv');valid=np.isfinite(a['max_relative_error'])
    ax.loglog(a['dt_s'][valid],100*a['max_relative_error'][valid],'o-',label='Ensayo de 2 s')
    ax.axhline(.1,color='gray',ls='--',label='Criterio local: 0,1 %')
    ax.set(xlabel='Paso de integración (s)',ylabel='Error relativo máximo (%)');ax.legend();save(fig,'energia-paso')

    fig,ax=setup();rows=table('performance-summary.csv')
    (ROOT/'presentacion/rendimiento.tex').write_text(performance_text(rows))
    for engine,label,marker in [('tp3','TP3: eventos','s'),('tp4','TP4: paso temporal','o')]:
        g=[r for r in rows if r['engine']==engine]
        ax.errorbar([int(r['n']) for r in g],[float(r['runtime_mean_s']) for r in g],
            yerr=[float(r['runtime_std_s']) for r in g],fmt=marker+'-',capsize=4,label=label)
    ax.set_yscale('log');ax.set(xlabel='Cantidad de partículas',ylabel='Tiempo de ejecución (s)');ax.legend()
    save(fig,'rendimiento')

    fig,ax=setup();rows=table('position-fu.csv')
    for x,label in [(.0175,r'$x_0=r$'),(.255,r'$x_0=0{,}255$ m'),(.4925,r'$x_0=R-r$')]:
        g=[r for r in rows if int(r['n'])==100 and float(r['obstacle_x_m'])==x]
        t=np.array([float(r['time_s']) for r in g]);y=np.array([float(r['fu_mean']) for r in g]);s=np.array([float(r['fu_std']) for r in g])
        ax.plot(t,y,label=label);ax.fill_between(t,np.maximum(0,y-s),np.minimum(1,y+s),alpha=.1)
    ax.axhline(.9,color='gray',ls='--');ax.set(xlabel='Tiempo (s)',ylabel='Fracción usada',ylim=(0,1.02));ax.legend(loc='lower right')
    save(fig,'posicion-fu')
    fig,ax=setup();rows=table('position-summary.csv')
    for n in [100,20]:
        g=[r for r in rows if int(r['n'])==n]
        ax.errorbar([float(r['obstacle_x_m']) for r in g],[float(r['t90_mean_s']) for r in g],
            yerr=[float(r['t90_std_s']) for r in g],fmt='o-',capsize=4,label=f'N={n}')
    ax.set(xlabel='Posición de los obstáculos (m)',ylabel='Tiempo al 90 % (s)');ax.legend();save(fig,'posicion-t90')

    fig,ax=setup();rows=table('speed-snapshots.csv')
    for t in [.1,.5,1,60]:
        g=[r for r in rows if float(r['time_s'])==t]
        edges=[float(r['v_left_m_s']) for r in g]+[float(g[-1]['v_right_m_s'])]
        ax.stairs([float(r['density_mean']) for r in g],edges,label=f't={t:g} s',linewidth=1.7)
    ax.axvline(1,color='gray',ls=':',label='t=0: rapidez unitaria')
    ax.set(xlabel='Rapidez (m/s)',ylabel='Densidad de\nprobabilidad (s/m)',xlim=(0,4));ax.legend();save(fig,'rapidez-evolucion')
    # Ajuste y error del ajuste lado a lado, como en el TP3 (método de la Teórica 0).
    small={'font.size':15,'axes.labelsize':15,'legend.fontsize':13}
    with plt.rc_context(small):
        fig,ax=setup(4.0,2.9);a=load('speed-stationary.csv');p=RESULTS/'speed-summary.json';SOURCES.add(p);s=json.loads(p.read_text())
        v=(a['v_left_m_s']+a['v_right_m_s'])/2
        ax.errorbar(v,a['density_mean'],yerr=a['density_std'],fmt='o',markersize=3,capsize=2,label='Simulación')
        x=np.linspace(0,4,300);theta=s['theta_fit_of_mean_J'];m=s['mass_kg']
        ax.plot(x,m*x/theta*np.exp(-m*x*x/(2*theta)),label='Ajuste')
        ax.set(xlabel='Rapidez (m/s)',ylabel='Densidad de\nprobabilidad (s/m)');ax.legend(loc='upper right');save(fig,'rapidez-ajuste')
        fig,ax=setup(4.0,2.9);o=load('speed-objective.csv')
        ax.plot(100*o['theta_J'],o['sse'],color=COLORS[0])
        best=np.argmin(np.abs(o['theta_J']-theta))
        ax.plot(100*theta,o['sse'][best],'o',color=COLORS[1],markersize=8,label='Mínimo')
        ax.axvline(100*s['theta_initial_reference_J'],color='gray',ls='--',label='$mv_0^2/2$')
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True));ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        ax.set(xlabel='$k_BT$ (10$^{-2}$ J)',ylabel='Error del ajuste\n((s/m)$^2$)',xticks=[1.2,1.25,1.3]);ax.legend(loc='upper center');save(fig,'rapidez-error')

    fig,ax=setup();rows=table('density-final-fu.csv')
    for n in [20,200,650]:
        g=[r for r in rows if int(r['n'])==n];t=np.array([float(r['time_s']) for r in g]);y=np.array([float(r['fu_mean']) for r in g]);sd=np.array([float(r['fu_std']) for r in g])
        ax.plot(t,y,label=f'N={n}');ax.fill_between(t,np.maximum(0,y-sd),np.minimum(1,y+sd),alpha=.1)
    ax.axhline(.9,color='gray',ls='--');ax.set(xlabel='Tiempo (s)',ylabel='Fracción usada',ylim=(0,1.02));ax.legend(loc='center right');save(fig,'densidad-fu')
    fig,axes=plt.subplots(1,2,figsize=(9,4.5),layout='constrained');rows=table('density-complete-summary.csv')
    for ax,key,label in zip(axes,['t90','t100'],['Tiempo al 90 % (s)','Tiempo al 100 % (s)']):
        g=[r for r in rows if r[key+'_mean_s']]
        ax.errorbar([float(r['density_m2']) for r in g],[float(r[key+'_mean_s']) for r in g],
            yerr=[float(r[key+'_std_s']) for r in g],fmt='o',capsize=4)
        g=[r for r in rows if not r[key+'_mean_s']]
        ax.scatter([float(r['density_m2']) for r in g],[float(r[key+'_mean_lower_bound_s']) for r in g],
                   marker='^',s=90,facecolors='none',edgecolors=COLORS[1])
        for r in g:
            ax.annotate(f"N={r['n']}\n> {float(r[key+'_mean_lower_bound_s']):.0f} s",
                        (float(r['density_m2']),float(r[key+'_mean_lower_bound_s'])),xytext=(8,-16),
                        textcoords='offset points',ha='right',va='top',fontsize=13,color=COLORS[1])
        ax.set(xlabel='Densidad (m⁻²)',ylabel=label,yscale='log');ax.grid(alpha=.2)
        # Marcas fijas: los rótulos automáticos del eje log dependen de la plataforma.
        ax.yaxis.set_major_locator(FixedLocator([2e1,3e1,5e1,1e2,2e2,3e2]))
        ax.yaxis.set_major_formatter(FuncFormatter(power_ten));ax.yaxis.set_minor_formatter(NullFormatter())
    save(fig,'densidad-tiempos')

    fig,ax=setup(8.5,4.4);rows=table('density-heatmap-summary.csv');counts=[20,50,100,200]
    positions=sorted({float(r['obstacle_x_m']) for r in rows});dx=positions[1]-positions[0]
    matrix=np.array([[float(next(r['t90_mean_s'] for r in rows if int(r['n'])==n and float(r['obstacle_x_m'])==x)) for x in positions] for n in counts])
    edges=np.r_[np.array(positions)-dx/2,positions[-1]+dx/2]
    image=ax.pcolormesh(edges,np.arange(5),matrix,cmap='viridis')
    for i,row in enumerate(matrix):
        j=int(np.argmin(row));ax.add_patch(Rectangle((positions[j]-dx/2,i),dx,1,fill=False,edgecolor='#ef4444',linewidth=3))
    ax.set(yticks=np.arange(4)+.5,yticklabels=counts,xlabel='Posición de los obstáculos (m)',ylabel='Cantidad de partículas',xticks=positions[::2])
    ax.tick_params(axis='x',rotation=30);fig.colorbar(image,ax=ax,label='Tiempo medio\nal 90 % (s)');save(fig,'mapa-posiciones')
    manifest=dict(sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SOURCES)},
                  builder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  figures={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*') if p.suffix in ['.png','.pdf']})
    (ROOT/'presentacion/.build/figures-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()
