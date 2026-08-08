"""Figura de una partícula seleccionada y sus vecinas."""

from __future__ import annotations

from pathlib import Path

from tp1viz.metrics import MetricsError
from tp1viz.particles import ParticleSystem


def plot_neighbors(
    system: ParticleSystem,
    neighbors: tuple[frozenset[int], ...],
    selected_id: int,
    cutoff: float,
    boundary: str,
    output: Path,
) -> None:
    """Dibuja los discos y destaca la partícula indicada y sus vecinas."""

    if selected_id <= 0 or selected_id > len(system.particles):
        raise MetricsError(
            f"particle debe estar entre 1 y {len(system.particles)}"
        )
    if cutoff < 0:
        raise MetricsError("rc no puede ser negativo")
    if boundary not in {"walls", "periodic"}:
        raise MetricsError("boundary debe ser walls o periodic")

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle, Patch, Rectangle
    except ModuleNotFoundError as error:
        raise MetricsError(
            "Matplotlib no está instalado; ejecutar "
            "pip install -r python/requirements.txt"
        ) from error

    selected = system.particles[selected_id - 1]
    selected_neighbors = neighbors[selected_id - 1]
    colors = {
        "other": "#c7cdd4",
        "neighbor": "#e6842a",
        "selected": "#176b87",
    }

    figure, axes = plt.subplots(figsize=(7, 7))
    axes.add_patch(
        Rectangle(
            (0, 0),
            system.side,
            system.side,
            facecolor="#f7f4ed",
            edgecolor="#293241",
            linewidth=1.5,
            zorder=0,
        )
    )
    axes.add_patch(
        Circle(
            (selected.x, selected.y),
            selected.radius + cutoff,
            fill=False,
            edgecolor=colors["selected"],
            linestyle="--",
            linewidth=1.2,
            alpha=0.65,
            zorder=1,
        )
    )

    for particle in system.particles:
        if particle.id == selected_id:
            category = "selected"
            zorder = 4
        elif particle.id in selected_neighbors:
            category = "neighbor"
            zorder = 3
        else:
            category = "other"
            zorder = 2
        axes.add_patch(
            Circle(
                (particle.x, particle.y),
                particle.radius,
                facecolor=colors[category],
                edgecolor="#293241",
                linewidth=0.55,
                zorder=zorder,
            )
        )
        if category != "other":
            axes.text(
                particle.x,
                particle.y,
                str(particle.id),
                ha="center",
                va="center",
                fontsize=6,
                color="white" if category == "selected" else "#293241",
                zorder=5,
            )

    boundary_label = "paredes" if boundary == "walls" else "periódico"
    axes.set_title(
        f"Partícula {selected_id} y sus {len(selected_neighbors)} vecinas\n"
        f"N={len(system.particles)}, L={system.side:g}, rc={cutoff:g}, "
        f"contorno {boundary_label}"
    )
    axes.set_xlabel("x")
    axes.set_ylabel("y")
    axes.set_xlim(0, system.side)
    axes.set_ylim(0, system.side)
    axes.set_aspect("equal", adjustable="box")
    axes.legend(
        handles=[
            Patch(facecolor=colors["selected"], label="Seleccionada"),
            Patch(facecolor=colors["neighbor"], label="Vecinas"),
            Patch(facecolor=colors["other"], label="Otras"),
        ],
        loc="upper right",
    )
    axes.grid(False)
    figure.tight_layout()

    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        figure.savefig(output, dpi=160)
    except (OSError, ValueError) as error:
        raise MetricsError(f"no se pudo escribir {output}: {error}") from error
    finally:
        plt.close(figure)
