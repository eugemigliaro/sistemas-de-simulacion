# Presentación del TP5

- `SdS_TP5_2026Q2G07CS_Presentacion.tex`: fuente Beamer, con el mismo formato que el TP4.
- `valores.tex`: números de los resultados. Lo genera `scripts/build_figures.py` desde `experiments/results`; no editarlo a mano. Lo que todavía no tiene datos aparece como "pendiente" en el PDF.
- `enlaces.json`: enlaces públicos de las cuatro animaciones (claves `atasco`, `tsdmd`, `edmd` e `hibrido`). `build_presentation.py` los escribe debajo de cada fotograma; mientras falten, dice "Enlace de YouTube pendiente".
- `figuras/`: figuras (PDF y PNG) y fotogramas de las animaciones (`anim-*.png`).
- `videos/`: los MP4 que se suben a YouTube y se embeben en el PPTX.
- `SdS_TP5_2026Q2G07CS_Presentacion.pptx`: versión para exponer, con las animaciones embebidas [GPRES, p. 2].
- `GUION.md`: lo que dice cada integrante en cada diapositiva, con tiempos.

El PDF que se entrega queda en `../entrega-final/SdS_TP5_2026Q2G07CS_Presentación.pdf`, y el ZIP del motor, en `../entrega-final/SdS_TP5_2026Q2G07CS_Codigo.zip`.

## Regenerar

Desde `entregas/tp5-evacuacion`:

```bash
make figures        # figuras y valores.tex
make videos         # MP4 y fotogramas
make presentation   # PDF oficial y PPTX
make delivery       # ZIP del motor
```

`build_presentation.py` busca `tectonic` en el PATH, en Homebrew o en `/usr/lib/chatgpt/resources/tectonic/tectonic`, y compila con `--only-cached`: solo se pueden usar los paquetes y bibliotecas de TikZ que ya están en la caché (por ejemplo, no están `calc` ni `decorations`).

## Antes de entregar

1. Correr los puntos c y d en una sola computadora (`make tiempos-c` y `make tiempos-d`) y regenerar.
2. Subir `videos/*.mp4` a YouTube (público o no listado), completar `enlaces.json` y regenerar.
3. Completar los `[pendiente]` del guion y las conclusiones.
4. Ensayar con el guion y cronometrar.
5. Probar el PPTX con los videos en la computadora de la exposición.
