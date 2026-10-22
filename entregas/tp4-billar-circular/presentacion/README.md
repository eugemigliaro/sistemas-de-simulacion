# Presentación del TP4

- `SdS_TP4_2026Q2G07CS_Presentacion.tex`: fuente Beamer, con el mismo formato que el TP3.
- `valores.tex`: números de los resultados. Lo genera `scripts/build_figures.py` desde `experiments/results`; no editarlo a mano.
- `enlaces.json`: enlaces públicos de las tres animaciones (claves `densidad`, `posicion` y `rapidez`). `build_presentation.py` los escribe debajo de cada fotograma; mientras falten, dice "Enlace de YouTube pendiente".
- `figuras/`: figuras (PDF) y fotogramas de las animaciones (PNG).
- `videos/`: los MP4 que se suben a YouTube y se embeben en el PPTX.
- `SdS_TP4_2026Q2G07CS_Presentacion.pptx`: versión para exponer, con las animaciones embebidas [GPRES, p. 2].
- `GUION.md`: lo que dice cada integrante en cada diapositiva, con tiempos.

El PDF que se entrega queda en `../entrega-final/SdS_TP4_2026Q2G07CS_Presentación.pdf`.

## Regenerar

Desde `entregas/tp4-billar-circular`:

```bash
make figures        # figuras y valores.tex
make videos         # MP4 y fotogramas
make presentation   # PDF oficial y PPTX
```

`build_presentation.py` busca `tectonic` en el PATH, en Homebrew o en `/usr/lib/chatgpt/resources/tectonic/tectonic`, y compila con `--only-cached`.

## Antes de entregar

1. Subir `videos/*.mp4` a YouTube (público o no listado), completar `enlaces.json` y regenerar.
2. Ensayar con el guion y cronometrar: el objetivo es 12 a 13 minutos.
3. Probar el PPTX con los videos en la computadora de la exposición.
