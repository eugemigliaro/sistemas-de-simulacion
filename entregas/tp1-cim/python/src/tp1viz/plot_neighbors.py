"""Figura de una partícula seleccionada y sus vecinas."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from tp1viz.metrics import MetricsError
from tp1viz.particles import ParticleSystem


COLORS = {
    "other": "#c7cdd4",
    "neighbor": "#e6842a",
    "selected": "#176b87",
}


def periodic_image_centers(
    x: float,
    y: float,
    radius: float,
    side: float,
) -> list[tuple[float, float]]:
    """Devuelve centros trasladados cuya circunferencia cruza el dominio."""

    x_shifts = [0.0]
    y_shifts = [0.0]
    if x - radius < 0:
        x_shifts.append(side)
    if x + radius > side:
        x_shifts.append(-side)
    if y - radius < 0:
        y_shifts.append(side)
    if y + radius > side:
        y_shifts.append(-side)
    return [
        (x + x_shift, y + y_shift)
        for x_shift in x_shifts
        for y_shift in y_shifts
        if x_shift != 0 or y_shift != 0
    ]


def _validate_inputs(
    system: ParticleSystem,
    neighbors: tuple[frozenset[int], ...],
    cutoff: float,
    boundary: str,
) -> None:
    if cutoff < 0:
        raise MetricsError("rc no puede ser negativo")
    if boundary not in {"walls", "periodic"}:
        raise MetricsError("boundary debe ser walls o periodic")
    if len(neighbors) != len(system.particles):
        raise MetricsError("la lista de vecinos no coincide con el sistema")


def _draw_neighbors(
    axes: Any,
    system: ParticleSystem,
    neighbors: tuple[frozenset[int], ...],
    selected_id: int | None,
    cutoff: float,
    boundary: str,
    *,
    interactive: bool,
) -> dict[Any, int]:
    from matplotlib.patches import Circle, Patch, Rectangle

    axes.clear()
    selected = (
        system.particles[selected_id - 1]
        if selected_id is not None
        else None
    )
    selected_neighbors = (
        neighbors[selected_id - 1]
        if selected_id is not None
        else frozenset()
    )
    artists: dict[Any, int] = {}

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
    if selected is not None:
        interaction_radius = selected.radius + cutoff
        interaction_centers = [(selected.x, selected.y)]
        if boundary == "periodic":
            interaction_centers.extend(
                periodic_image_centers(
                    selected.x,
                    selected.y,
                    interaction_radius,
                    system.side,
                )
            )
        for center in interaction_centers:
            axes.add_patch(
                Circle(
                    center,
                    interaction_radius,
                    fill=False,
                    edgecolor=COLORS["selected"],
                    linestyle="--",
                    linewidth=1.2,
                    alpha=(
                        0.65 if center == interaction_centers[0] else 0.45
                    ),
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
        circle = Circle(
            (particle.x, particle.y),
            particle.radius,
            facecolor=COLORS[category],
            edgecolor="#293241",
            linewidth=0.55,
            zorder=zorder,
        )
        if interactive:
            circle.set_picker(5)
            artists[circle] = particle.id
        axes.add_patch(circle)
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
    if selected_id is None:
        axes.set_title(
            "Hacé clic sobre una partícula para analizarla\n"
            f"N={len(system.particles)}, L={system.side:g}, rc={cutoff:g}, "
            f"contorno {boundary_label}"
        )
    else:
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
    legend_handles = [
        Patch(facecolor=COLORS["selected"], label="Seleccionada"),
        Patch(facecolor=COLORS["neighbor"], label="Vecinas"),
        Patch(facecolor=COLORS["other"], label="Otras"),
    ]
    if boundary == "periodic" and selected is not None:
        legend_handles.append(
            Patch(
                facecolor="none",
                edgecolor=COLORS["selected"],
                linestyle="--",
                alpha=0.45,
                label="Alcance periódico",
            )
        )
    axes.legend(handles=legend_handles, loc="upper right")
    axes.grid(False)
    return artists


def plot_neighbors(
    system: ParticleSystem,
    neighbors: tuple[frozenset[int], ...],
    selected_id: int,
    cutoff: float,
    boundary: str,
    output: Path,
) -> None:
    """Dibuja los discos y destaca la partícula indicada y sus vecinas."""

    _validate_inputs(system, neighbors, cutoff, boundary)
    if selected_id <= 0 or selected_id > len(system.particles):
        raise MetricsError(
            f"particle debe estar entre 1 y {len(system.particles)}"
        )

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as error:
        raise MetricsError(
            "Matplotlib no está instalado; ejecutar "
            "pip install -r python/requirements.txt"
        ) from error

    figure, axes = plt.subplots(figsize=(7, 7))
    _draw_neighbors(
        axes,
        system,
        neighbors,
        selected_id,
        cutoff,
        boundary,
        interactive=False,
    )
    figure.tight_layout()

    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        figure.savefig(output, dpi=160)
    except (OSError, ValueError) as error:
        raise MetricsError(f"no se pudo escribir {output}: {error}") from error
    finally:
        plt.close(figure)


def show_neighbors_interactive(
    system: ParticleSystem,
    neighbors: tuple[frozenset[int], ...],
    cutoff: float,
    boundary: str,
) -> None:
    """Abre una ventana y actualiza la selección al hacer clic en un disco."""

    _validate_inputs(system, neighbors, cutoff, boundary)
    try:
        import matplotlib

        if sys.platform == "darwin":
            matplotlib.use("MacOSX")
        import matplotlib.pyplot as plt
    except (ImportError, ModuleNotFoundError) as error:
        raise MetricsError(
            "no se pudo abrir la interfaz de Matplotlib; verificar la "
            "instalación gráfica de Python"
        ) from error

    figure, axes = plt.subplots(figsize=(8, 8))
    figure.canvas.manager.set_window_title("Explorador de vecinos TP1")
    artists: dict[Any, int] = {}

    def redraw(selected_id: int | None) -> None:
        nonlocal artists
        artists = _draw_neighbors(
            axes,
            system,
            neighbors,
            selected_id,
            cutoff,
            boundary,
            interactive=True,
        )
        figure.tight_layout()
        figure.canvas.draw_idle()

    def select_particle(event: Any) -> None:
        selected_id = artists.get(event.artist)
        if selected_id is not None:
            redraw(selected_id)

    figure.canvas.mpl_connect("pick_event", select_particle)
    redraw(None)
    plt.show()
