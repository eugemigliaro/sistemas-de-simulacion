# TP2 — Bandadas de agentes autopropulsados

Resolución reproducible del Trabajo Práctico 2 de Sistemas de Simulación. El motor se implementa en C++20 y la animación y el análisis se ejecutarán como programas independientes en Python 3, según exige la consigna [TP02, p. 1].

## Estado

En desarrollo. La primera fase implementa y prueba:

- geometría periódica para partículas puntuales;
- búsqueda de vecinas por fuerza bruta y Cell Index Method;
- polarización `va` y fracción de la componente gigante `S`;
- actualización sincrónica de Vicsek y del modelo votante.

## Convenciones principales

- Caja periódica de lado `L = 10`, rapidez `v = 0.03`, radio de interacción `rc = 1` y paso `dt = 1` [T02, pp. 40–42].
- `eta` se normaliza en `[0,1]` y el ruido se sortea uniformemente en `[-eta*pi, eta*pi]`, como en la referencia del votante [B09, p. 3]. La misma convención se usa en ambos modelos para compararlos.
- En ambos modelos la propia partícula pertenece al vecindario de alineación. En el votante también puede ser elegida como candidata a copiar; es una decisión explícita de esta resolución.
- Todas las partículas leen el estado anterior y se actualizan simultáneamente.

Las decisiones completas y las diferencias respecto de las fuentes están en [`docs/decisiones.md`](docs/decisiones.md).

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
  --M 9 --trajectory-every 10 \
  --trajectory data/generated/trajectory.csv \
  --observables data/generated/observables.csv
```

El CSV de trayectoria guarda posiciones, velocidades y ángulos para la animación. El CSV de observables guarda `va`, `S`, tiempo del CIM, pares vecinos y evaluaciones de distancia para cada estado.

## Análisis independiente

El análisis estadístico básico usa solo la biblioteca estándar. Las figuras y animaciones requieren `matplotlib` y `pillow`:

```bash
python3 -m venv python/.venv
python/.venv/bin/pip install -r python/requirements.txt
```

Ejemplo de resumen estacionario:

```bash
PYTHONPATH=python/src python3 -m tp2analysis summary \
  --stationary-start 500 \
  --output experiments/results/summary.csv \
  experiments/raw/*.csv
```

El resumen primero promedia el intervalo estacionario dentro de cada semilla y después calcula media y desvío muestral entre realizaciones independientes.

## Barrido piloto

```bash
make release
python3 scripts/run_sweep.py experiments/configs/pilot.json
```

El piloto usa pocos valores de ruido y solo dos semillas para localizar regiones interesantes; no se considera evidencia final.
