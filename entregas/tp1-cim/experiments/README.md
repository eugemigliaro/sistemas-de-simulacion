# Experimentos

- configs/: parámetros reproducibles de cada estudio.
- raw/: mediciones individuales regenerables, ignoradas por Git.
- figures/: figuras finales seleccionadas.

Los experimentos de rendimiento se habilitarán únicamente después de que fuerza bruta y CIM produzcan resultados idénticos en las pruebas diferenciales.

`benchmark-m` escribe las repeticiones individuales en `raw/metrics-m.csv`. El comando Python `plot-m` genera `raw/summary-m.csv` y una figura en `figures/`. Los archivos de `raw/` son regenerables y están ignorados por Git; las figuras finales seleccionadas pueden versionarse.
