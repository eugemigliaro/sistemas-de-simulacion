"""Tres situaciones del sistema 2.2; animacion fisica independiente del motor."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND","Agg")
os.environ.setdefault("MPLCONFIGDIR",str(ROOT/"python/.matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME",str(ROOT/"python/.cache"))
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation,PillowWriter
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Circle
import numpy as np

from billiard_analysis import frames


def main():
    config=json.loads((ROOT/"experiments/configs/obstacle-position.json").read_text())
    dt=json.loads((ROOT/"experiments/results/position-step-validation.json").read_text())["study_dt"]
    raw=ROOT/"experiments/raw/obstacle-position"
    figures=ROOT/"experiments/figures"
    binary=ROOT/"cpp/build/release/tp4"
    sequences=[];runs=[]
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    for i,x in enumerate(config["representative_positions_m"]):
        path=raw/f"animation-x{i}.csv"
        command=[str(binary),"billiard","--n","100","--duration","5","--dt",str(dt),
            "--save-every",str(round(.025/dt)),"--seed","1","--obstacles","1", "--obstacle-x",str(x),"--output",str(path)]
        subprocess.run(command,check=True)
        metadata=json.loads(Path(str(path)+".json").read_text())
        sequences.append(list(frames(path,metadata)))
        runs.append(dict(x=x,trajectory=str(path.relative_to(ROOT)),sha256=digest(path),metadata=metadata,
                         command=[str(binary.relative_to(ROOT)),*command[1:-1],str(path.relative_to(ROOT))]))
    fig,axes=plt.subplots(1,3,figsize=(12,4.5))
    fig.subplots_adjust(top=.82,bottom=.2,wspace=.3)
    collections=[]
    for ax,x in zip(axes,config["representative_positions_m"]):
        ax.add_patch(Circle((0,0),.51,fill=False,color="black",linewidth=1))
        for ox in [-x,x]:ax.add_patch(Circle((ox,0),.0175,color="black"))
        collection=PatchCollection([],edgecolors="none");ax.add_collection(collection);collections.append(collection)
        ax.set(xlim=(-.535,.535),ylim=(-.535,.535),aspect="equal",xlabel="x (m)",ylabel="y (m)",title=f"x₀={x:g} m")
    title=fig.suptitle("")
    fig.legend(handles=[Line2D([],[],linestyle="none",marker="o",color=c,label=l)
        for c,l in [("#1f77b4","Frescas"),("#d62728","Usadas"),("black","Obstáculos")]],
        loc="lower center",ncol=3,frameon=False,bbox_to_anchor=(.5,.015))
    def update(index):
        for collection,sequence in zip(collections,sequences):
            state=sequence[index][2]
            collection.set_paths([Circle(tuple(p),.0175) for p in state[:,3:5]])
            collection.set_facecolor(np.where(state[:,7,None]==0,np.array([.12,.47,.71,1]),np.array([.84,.15,.16,1])))
        title.set_text(f"N=100 · t={sequences[0][index][1]:.3f} s")
        return (*collections,title)
    movie=FuncAnimation(fig,update,frames=len(sequences[0]),init_func=lambda:(),interval=40,cache_frame_data=False)
    gif=figures/"position-demo.gif";png=figures/"position-demo.png"
    movie.save(gif,writer=PillowWriter(fps=25),dpi=80)
    fig.savefig(png,dpi=150);plt.close(fig)
    manifest=dict(runs=runs,source_sha256=digest(Path(__file__)),binary_sha256=digest(binary),
        artifacts={str(p.relative_to(ROOT)):digest(p) for p in [gif,png]},
        note="Cinco segundos de una realizacion por posicion; no promedio ni archivos para entregar")
    (ROOT/"experiments/results/position-animation-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")


if __name__=="__main__":main()
