"""Demostraciones físicas independientes; no se animan gráficos de observables."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
from billiard_analysis import frames
os.environ.setdefault('MPLBACKEND','Agg')
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'python/.matplotlib'))
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation,PillowWriter


def position_media(out):
    source=json.loads((ROOT/'experiments/results/position-animation-manifest.json').read_text())
    fig,axes=plt.subplots(1,3,figsize=(12,4.3),layout='constrained')
    datasets=[];artists=[]
    for ax,run in zip(axes,source['runs']):
        path=ROOT/run['trajectory']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==run['sha256']
        meta=run['metadata'];data=list(frames(path,meta));datasets.append((meta,data))
        ax.set(xlim=(-.54,.54),ylim=(-.54,.54),aspect='equal');ax.axis('off')
        ax.add_patch(Circle((0,0),meta['radius'],fill=False,color='black',linewidth=2))
        for x in [-meta['obstacle_x'],meta['obstacle_x']]:
            ax.add_patch(Circle((x,0),meta['particle_radius'],color='black'))
        fig.canvas.draw();diameter=2*meta['particle_radius']/1.08*ax.bbox.width*72/fig.dpi
        scatter=ax.scatter([],[],s=diameter**2,edgecolors='none')
        title=ax.set_title('',fontsize=20);artists.append((scatter,title))
    def update(j):
        for (meta,data),(scatter,title) in zip(datasets,artists):
            _,t,state=data[j];scatter.set_offsets(state[:,3:5])
            scatter.set_facecolor(np.where(state[:,7,None]==0,np.array([0,.36,.57,1]),np.array([.8,.15,.15,1])))
            title.set_text(f"x₀={meta['obstacle_x']:.4f} m\nt={t:.2f} s")
    gif=out/'videos/posicion.gif'
    FuncAnimation(fig,update,frames=len(datasets[0][1]),interval=40).save(gif,writer=PillowWriter(fps=25),dpi=100)
    update(100);fig.savefig(out/'figuras/anim-posicion.png',dpi=140);plt.close(fig)
    return dict(source='experiments/results/position-animation-manifest.json',physical_duration_s=5,
        playback='1.6 veces mas lento',trajectory_sha256={r['trajectory']:r['sha256'] for r in source['runs']},
        gif_sha256=hashlib.sha256(gif.read_bytes()).hexdigest())


def main():
    out=ROOT/'presentacion';raw=out/'.build/media';raw.mkdir(parents=True,exist_ok=True)
    binary=ROOT/'cpp/build/release/tp4'
    if '--position-only' in sys.argv:
        manifest=json.loads((out/'.build/media-manifest.json').read_text())
        manifest['posicion']=position_media(out)
        (out/'.build/media-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        return
    studies=[('energia',[(300,1,False,None)],.00005),
        ('rendimiento',[(20,2,True,None),(650,2,True,'initial-n650-seed2.csv')],.00005),
        ('rapidez',[(100,1,False,None)],.0000125),
        ('densidad',[(50,1,True,None),(650,1,True,'initial-n650-seed1.csv')],.0000125)]
    manifest={}
    for name,systems,dt in studies:
        datasets=[];commands=[]
        for n,seed,obstacles,initial in systems:
            path=raw/f'{name}-{n}.csv'
            cmd=[str(binary),'billiard','--n',str(n),'--seed',str(seed),'--duration','1',
                '--dt',str(dt),'--save-every',str(round(.01/dt)),
                '--obstacles',str(int(obstacles)),'--obstacle-x','0.0175','--output',str(path)]
            if initial:cmd+=['--initial',str(ROOT/'experiments/raw/density-position'/initial)]
            if not path.exists():subprocess.run(cmd,check=True,capture_output=True,text=True)
            meta=json.loads(Path(str(path)+'.json').read_text())
            data=list(frames(path,meta));datasets.append((meta,data));commands.append(cmd)
        fig,axes=plt.subplots(1,len(systems),figsize=(5*len(systems),4.3),squeeze=False,layout='constrained')
        artists=[]
        for ax,(meta,data) in zip(axes[0],datasets):
            ax.set(xlim=(-.54,.54),ylim=(-.54,.54),aspect='equal');ax.axis('off')
            ax.add_patch(Circle((0,0),meta['radius'],fill=False,color='black',linewidth=2))
            if meta['obstacles']:
                for x in [-.0175,.0175]:ax.add_patch(Circle((x,0),meta['particle_radius'],color='black'))
            fig.canvas.draw();diameter=2*meta['particle_radius']/(1.08)*ax.bbox.width*72/fig.dpi
            scatter=ax.scatter([],[],s=diameter**2,edgecolors='none')
            title=ax.set_title('',fontsize=21);artists.append((scatter,title))
        def update(j):
            for (meta,data),(scatter,title) in zip(datasets,artists):
                _,t,state=data[j];scatter.set_offsets(state[:,3:5])
                scatter.set_facecolor(np.where(state[:,7,None]==0,np.array([0,.36,.57,1]),np.array([.8,.15,.15,1])))
                title.set_text(f"N={meta['n']}     t={t:.2f} s")
        movie=FuncAnimation(fig,update,frames=len(datasets[0][1]),interval=40)
        gif=out/'videos'/f'{name}.gif';movie.save(gif,writer=PillowWriter(fps=25),dpi=100)
        update(50);poster=out/'figuras'/f'anim-{name}.png';fig.savefig(poster,dpi=140);plt.close(fig)
        manifest[name]=dict(commands=commands,physical_duration_s=1,playback='4 veces mas lento',
            trajectory_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.glob(name+'*.csv')},
            gif_sha256=hashlib.sha256(gif.read_bytes()).hexdigest())
    manifest['posicion']=position_media(out)
    (out/'.build/media-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()
