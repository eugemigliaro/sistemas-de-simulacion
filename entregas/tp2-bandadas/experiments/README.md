# Experimentos

## Etapas

1. **Piloto:** localizar la caída de polarización y observar escalas de relajación con pocos valores de `eta` y dos semillas. Sus resultados no son finales.
2. **Calibración:** elegir tiempos de descarte, duración y malla refinada mediante series temporales y medias por bloques.
3. **Producción:** ejecutar suficientes realizaciones independientes y generar resúmenes con media y desvío.
4. **Casos visuales:** guardar trayectorias solo para situaciones características de cada estudio.

El piloto se ejecuta con:

```bash
make release
python3 scripts/run_sweep.py experiments/configs/pilot.json
```

Los archivos crudos quedan ignorados por Git en `experiments/raw/`. Cada fila conserva modelo, densidad, ruido, semilla y tiempo.

Las conclusiones provisionales del primer barrido están en [`pilot-findings.md`](pilot-findings.md).

## Criterio estadístico

Para cada corrida se descarta el transitorio y se promedian `va(t)` y `S(t)` en el intervalo estacionario. Después se calculan media y desvío muestral entre semillas. Los instantes correlacionados de una misma corrida no se tratan como realizaciones independientes [T00, p. 69].

La selección del inicio estacionario debe justificarse con series temporales y una línea vertical en las figuras [TP02, p. 2].
