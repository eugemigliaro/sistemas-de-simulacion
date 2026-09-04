# Experimentos

## Etapas

1. **Piloto:** localizar la caída de polarización y observar escalas de relajación con pocos valores de `eta` y dos semillas. Sus resultados no son finales.
2. **Calibración:** elegir tiempos de descarte, duración y malla refinada mediante series temporales y medias por bloques.
3. **Producción:** ejecutar suficientes realizaciones independientes y generar resúmenes con media y desvío.
4. **Casos visuales:** guardar trayectorias solo para situaciones características de cada modelo.

El estudio de clusters agrega, por indicación oral de la cátedra, las densidades nominales `1/pi`, `1/(2*pi)` y `1/(3*pi)` [N-2026-08-22-densidades-s-tp2]. Con `L = 10` se adoptan `N = 32`, `16` y `11`, es decir densidades reales `0.32`, `0.16` y `0.11`. Las leyendas de los gráficos muestran las densidades reales.

## Configuraciones disponibles

| Archivo | Propósito | Estado |
|---|---|---|
| `configs/pilot.json` | `rho = 2, 4, 8`, ambos modelos | ejecutado con el CSV actual |
| `configs/cluster-low-density.json` | densidades bajas para `S` | ejecutado con el CSV actual |
| `configs/calibration.json` | mallas refinadas y corridas más largas | pendiente |
| `configs/production.example.json` | plantilla para resultados principales | no definitiva |
| `configs/cluster-production.example.json` | plantilla para resultados de clusters | no definitiva |
| `configs/visual-cases.json` | cuatro animaciones características | lista para ejecutar |

Los pilotos se ejecutan con:

```bash
make release
python3 scripts/run_sweep.py experiments/configs/pilot.json
python3 scripts/run_sweep.py experiments/configs/cluster-low-density.json
```

Los archivos actuales quedan en `experiments/raw/pilot-metadata-v2/` y `experiments/raw/cluster-low-density-metadata-v2/`. El sufijo distingue estas corridas de pilotos antiguos que no incluían todos los metadatos. Cada directorio contiene el `manifest.json` exacto de su barrido. Si cambia la configuración, se debe elegir otro `output_dir`; `--force` solo vuelve a ejecutar la misma configuración.

Los casos visuales se generan con:

```bash
python3 scripts/run_visual_cases.py experiments/configs/visual-cases.json
```

Cada GIF usa el CSV de trayectoria y el CSV de observables de la misma corrida. El script informa las unidades simuladas por segundo para que la velocidad de reproducción no quede implícita.

Las conclusiones provisionales del primer barrido están en [`pilot-findings.md`](pilot-findings.md). El procedimiento completo de calibración y producción está en [`../docs/protocolo-experimental.md`](../docs/protocolo-experimental.md).

## Criterio estadístico

Para cada corrida se descarta el transitorio y se promedian `va(t)` y `S(t)` en el intervalo estacionario. Después se calculan media y desvío muestral entre semillas. Los instantes correlacionados de una misma corrida no se tratan como realizaciones independientes [T00, p. 69].

La selección del inicio estacionario debe justificarse con series temporales, medias por bloques completos y una línea vertical en las figuras [TP02, p. 2]. El analizador rechaza tiempos repetidos, corridas truncadas y mezclas de parámetros físicos.
