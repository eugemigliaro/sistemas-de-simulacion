"""Animaciones de la presentación: MP4 en presentacion/videos y su fotograma (anim-*.png)
en presentacion/figuras [GPRES, pp. 2-3]. Lee los cuadros de experiments/raw/animaciones;
se omite cada animación cuya corrida falte o no haya terminado.

Uso: python scripts/build_videos.py [atasco|tsdmd|edmd|hibrido ...]
"""
from __future__ import annotations

import sys

from common import FIGURES, RAW, T_STAR, VIDEOS, complete
from tp5analysis.animation import animate

# nombre: (corrida, opciones de animate)
ANIMATIONS = {
    "atasco": ("atasco_seed405.txt", dict(every=5, color="speed", poster_time=300.0,
                                          caption="TSDMD, N = 200: el arco queda quieto y nadie más sale (15× tiempo real)")),
    "tsdmd": ("tsdmd_seed401.txt", dict(every=5, color="speed", poster_time=150.0,
                                        caption="TSDMD, N = 200: evacuación completa (15× tiempo real)")),
    "edmd": ("edmd_seed401.txt", dict(every=5, color="speed", poster_time=150.0,
                                      caption="EDMD puro, N = 200 (15× tiempo real)")),
    "hibrido": ("hybrid_seed401.txt", dict(every=1, color="mode", until=60.0, poster_time=12.0,
                                           caption=f"Híbrido, T* = {T_STAR:g} s: los primeros 60 s (3× tiempo real)".replace(".", ","))),
}


def main() -> None:
    names = sys.argv[1:] or list(ANIMATIONS)
    VIDEOS.mkdir(parents=True, exist_ok=True)
    for name in names:
        source, options = ANIMATIONS[name]
        path = RAW / "animaciones" / source
        if not complete(path):
            print(f"falta {path.name}: se omite la animación {name}")
            continue
        animate(path, VIDEOS / f"{name}.mp4", fps=30, poster=FIGURES / f"anim-{name}.png", **options)
        print(f"{name}: {(VIDEOS / f'{name}.mp4').stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
