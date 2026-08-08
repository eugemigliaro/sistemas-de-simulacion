# Experimentos

- configs/: parámetros reproducibles de cada estudio.
- raw/: mediciones individuales regenerables, ignoradas por Git.
- figures/: figuras finales seleccionadas.
- results/: resúmenes CSV seleccionados y versionados.

Los experimentos de rendimiento se habilitarán únicamente después de que fuerza bruta y CIM produzcan resultados idénticos en las pruebas diferenciales.

`benchmark-m` escribe las repeticiones individuales en `raw/metrics-m.csv`. El comando Python `plot-m` genera `raw/summary-m.csv` y una figura en `figures/`. Los archivos de `raw/` son regenerables y están ignorados por Git; las figuras finales seleccionadas pueden versionarse.

La fase 7 conserva la calibración en `configs/phase7-calibration.json`, los resúmenes en `results/` y cuatro figuras finales en `figures/`. El protocolo y la interpretación están en `../docs/fase-7-experimento-m.md`.

La fase 8 se configura mediante `configs/phase8-n.json`. Los resúmenes `summary-n-walls.csv` y `summary-n-periodic.csv` comparan densidad libre y fija. Las figuras `time-vs-n-*.png` muestran las curvas en escalas lineal y logarítmica. La interpretación integrada está en `../informe-final.md`.
