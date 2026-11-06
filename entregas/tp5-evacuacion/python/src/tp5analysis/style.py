"""Estilo de las figuras, el mismo del TP4: ejes en palabras con unidades, sin títulos ni
captions, tipografía grande y puntos con símbolo [GPRES, pp. 1-2]."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE, ORANGE, AQUA, YELLOW, PURPLE = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#7b4fc9"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#dddcd8"
EVENT, STEP = BLUE, ORANGE  # EDMD y TSDMD en todas las figuras

plt.rcParams.update({
    "font.size": 20, "axes.labelsize": 22, "legend.fontsize": 18, "xtick.labelsize": 19, "ytick.labelsize": 19,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "lines.linewidth": 2.0, "lines.markersize": 9, "legend.frameon": False,
    "savefig.bbox": "tight", "mathtext.default": "regular", "axes.formatter.use_locale": False,
})


def comma(value: float, decimals: int = 0) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


def comma_axis(axis, which: str = "both") -> None:
    """Coma decimal en los ejes."""
    fmt = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    if which in ("x", "both"):
        axis.xaxis.set_major_formatter(fmt)
    if which in ("y", "both"):
        axis.yaxis.set_major_formatter(fmt)


def save(figure, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path.with_suffix(".pdf"))
    figure.savefig(path.with_suffix(".png"), dpi=150)
    plt.close(figure)
