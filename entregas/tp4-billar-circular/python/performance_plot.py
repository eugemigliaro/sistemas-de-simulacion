"""Revisión visual del análisis de censura, sin repetir mediciones de rendimiento."""
import csv
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "python/.matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / "python/.cache"))
import matplotlib.pyplot as plt


def main():
    source = ROOT / "experiments/results/density-summary.csv"
    with source.open() as handle:
        rows = list(csv.DictReader(handle))
    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    for obs, label, color, size in [("t90", "t₉₀", "#0072B2", 140), ("t100", "t₁₀₀", "#D55E00", 40)]:
        observed = [r for r in rows if r[obs + "_mean_s"]]
        if observed:
            ax.errorbar([float(r["density_m2"]) for r in observed],
                        [float(r[obs + "_mean_s"]) for r in observed],
                        yerr=[float(r[obs + "_std_s"]) for r in observed],
                        fmt="o", capsize=4, color=color, label=f"{label}: media ± desvío estándar")
        censored = [r for r in rows if not r[obs + "_mean_s"]]
        if censored:
            ax.scatter([float(r["density_m2"]) for r in censored],
                       [float(r[obs + "_mean_lower_bound_s"]) for r in censored],
                       marker="^", s=size, facecolors="none" if obs == "t90" else color,
                       edgecolors=color, linewidths=1.6,
                       label=f"{label}: cota inferior (censura)")
    ax.set(xlabel="Densidad N/(πR²) (m⁻²)", ylabel="Tiempo de conversión o cota inferior (s)",
           title="Obstáculos en contacto · corte a 30 s")
    ax.legend(fontsize=10); ax.grid(alpha=.2)
    output = ROOT / "experiments/figures/conversion-vs-density.png"
    fig.savefig(output, dpi=180); plt.close(fig)
    manifest_path = ROOT / "experiments/results/performance-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest["artifacts"][str(output.relative_to(ROOT))] = digest(output)
    manifest["density_plot_revision"] = dict(source=str(Path(__file__).relative_to(ROOT)),
        source_sha256=digest(Path(__file__)), data_sha256=digest(source),
        command="python python/performance_plot.py", reason="mostrar cotas coincidentes sin ocultarlas; omitir leyendas de medias no observadas")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__": main()
