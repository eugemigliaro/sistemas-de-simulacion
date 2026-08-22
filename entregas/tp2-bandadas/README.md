# TP2 — Bandadas de agentes autopropulsados

Resolución reproducible del Trabajo Práctico 2 de Sistemas de Simulación. El motor está implementado en C++20 y la animación y el análisis son programas independientes en Python 3, como exige la consigna [TP02, p. 1].

## Estado

El motor, los observables, el análisis, las animaciones y la automatización experimental están implementados y probados. Todavía no se consideran cerrados los resultados numéricos finales: primero hay que ejecutar la calibración, justificar el inicio estacionario y recién entonces fijar la configuración de producción.

## Convenciones principales

- Caja periódica de lado `L = 10`, rapidez `v = 0.03`, radio de interacción `rc = 1` y paso `dt = 1` [T02, pp. 40–42].
- `eta` se normaliza en `[0,1]` y el ruido se sortea uniformemente en `[-eta*pi, eta*pi]`, como en la referencia del votante [B09, p. 3]. La misma convención se usa en ambos modelos para compararlos.
- En ambos modelos la propia partícula pertenece al vecindario de alineación. En el votante también puede ser elegida como candidata a copiar.
- Todas las partículas leen el estado anterior y se actualizan simultáneamente.

Las decisiones completas y las diferencias respecto de las fuentes están en [`docs/decisiones.md`](docs/decisiones.md). El protocolo para pasar de piloto a resultados finales está en [`docs/protocolo-experimental.md`](docs/protocolo-experimental.md).

## Compilación y pruebas

```bash
make test
make sanitize
make visual-test  # requiere matplotlib y Pillow
```

Ejemplo mínimo:

```bash
make debug
./cpp/build/debug/tp2 simulate \
  --model vicsek --rho 2 --eta 0.25 --steps 1000 --seed 1 \
  --M 9 --trajectory-every 2 \
  --trajectory data/generated/trajectory.csv \
  --observables data/generated/observables.csv
```

Los dos CSV registran `model`, `density`, `particle_count`, `side`, `cells_per_side`, `cutoff`, `speed`, `time_step`, `eta` y `seed`. Así, Python puede rechazar archivos de corridas incompatibles. El formato anterior, sin metadatos físicos, no se admite; los pilotos ya fueron regenerados con el formato actual.

## Animación

La animación muestra las partículas con color según su ángulo y, en el mismo cuadro, la historia acumulada de `va(t)` y `S(t)` junto con sus valores actuales:

```bash
PYTHONPATH=python/src python3 -m tp2analysis animate \
  --input data/generated/trajectory.csv \
  --observables data/generated/observables.csv \
  --fps 5 \
  --output data/generated/animation.gif
```

La rapidez percibida se controla con dos parámetros. La cantidad de unidades simuladas mostradas por segundo es:

```text
trajectory_every * dt * fps
```

Por ejemplo, `trajectory_every = 2`, `dt = 1` y `fps = 5` muestran 10 unidades simuladas por segundo. Para ralentizar aún más se puede usar `--fps 3` o guardar más cuadros con `--trajectory-every 1`.

Los cuatro casos visuales preconfigurados se generan con:

```bash
make release
python3 scripts/run_visual_cases.py experiments/configs/visual-cases.json
```

## Análisis independiente

El análisis estadístico básico usa solo la biblioteca estándar. Las figuras y animaciones requieren `matplotlib` y `pillow`:

```bash
python3 -m venv python/.venv
python/.venv/bin/pip install -r python/requirements.txt
```

Para inspeccionar una corrida y comparar medias por bloques completos:

```bash
PYTHONPATH=python/src python3 -m tp2analysis timeseries \
  experiments/raw/pilot-metadata-v2/vicsek-rho4-eta0p5-seed1-observables.csv \
  --stationary-start 300 \
  --output data/generated/timeseries.png

PYTHONPATH=python/src python3 -m tp2analysis blocks \
  experiments/raw/pilot-metadata-v2/vicsek-rho4-eta0p5-seed1-observables.csv \
  --block-size 200 --start 0 \
  --output data/generated/blocks.csv \
  --plot data/generated/blocks.png
```

Una vez elegido el descarte, el resumen primero promedia el intervalo estacionario dentro de cada semilla y después calcula media y desvío muestral entre realizaciones independientes:

```bash
PYTHONPATH=python/src python3 -m tp2analysis summary \
  experiments/raw/pilot-metadata-v2/*-observables.csv \
  --stationary-start 800 \
  --output data/generated/summary.csv

PYTHONPATH=python/src python3 -m tp2analysis plot-eta \
  --input data/generated/summary.csv \
  --observable polarization \
  --output data/generated/va-vs-eta.png

PYTHONPATH=python/src python3 -m tp2analysis plot-va-s \
  --input data/generated/summary.csv \
  --output data/generated/va-vs-s.png
```

Si cada combinación necesita un descarte distinto, `--stationary-starts archivo.csv` reemplaza a `--stationary-start`. El archivo debe tener exactamente las columnas `model,density,eta,stationary_start` y una fila por combinación analizada.

## Comparación del CIM con el TP1

```bash
PYTHONPATH=python/src python3 -m tp2analysis cim-summary \
  experiments/raw/pilot-metadata-v2/*-observables.csv \
  --start 100 \
  --output data/generated/cim-summary.csv

PYTHONPATH=python/src python3 -m tp2analysis plot-cim \
  --input data/generated/cim-summary.csv \
  --tp1 ../tp1-cim/experiments/results/summary-n-periodic.csv \
  --output data/generated/cim-comparison.png
```

La figura es una comparación orientativa de las implementaciones: TP1 y TP2 no usan exactamente la misma densidad ni el mismo trabajo por paso.

## Barridos y entrega de código

```bash
make release
python3 scripts/run_sweep.py experiments/configs/pilot.json
python3 scripts/run_sweep.py experiments/configs/cluster-low-density.json
```

Cada directorio de salida contiene un `manifest.json`; el script impide mezclar configuraciones distintas. `calibration.json` es el siguiente barrido previsto. Los archivos `production.example.json` y `cluster-production.example.json` son plantillas y no deben ejecutarse como producción definitiva hasta cerrar la calibración.

Para crear un ZIP que contenga únicamente el código fuente y el Makefile del motor C++:

```bash
python3 scripts/package_code.py --output data/generated/tp2-codigo.zip
```
