# Automatización

`calibrate_n.py` determina el mayor múltiplo de un paso que el generador puede construir para todas las semillas indicadas, por separado para paredes y periodicidad. Desde la carpeta del TP:

    python/.venv/bin/python scripts/calibrate_n.py \
      --binary cpp/build/release/tp1 \
      --output experiments/configs/phase7-calibration.json \
      --seeds 42 31415 20260807 \
      --attempts 100000 \
      --step 50

`run_n_experiments.py` genera y mide los 44 sistemas definidos en `experiments/configs/phase8-n.json`:

    python/.venv/bin/python scripts/run_n_experiments.py \
      --binary cpp/build/release/tp1 \
      --config experiments/configs/phase8-n.json \
      --output-root experiments/raw/phase8-random \
      --results-root experiments/results

`run_m_experiments.py` ejecuta el barrido completo de M. Cada repetición crea una semilla aleatoria única y usa el mismo sistema para comparar todos los M:

    python/.venv/bin/python scripts/run_m_experiments.py \
      --binary cpp/build/release/tp1 \
      --config experiments/configs/phase7-calibration.json \
      --output-root experiments/raw/phase7-random \
      --results-root experiments/results \
      --repetitions 100

`demo.py` permite variar todos los parámetros relevantes durante la exposición, crea la lista completa y abre un explorador donde las partículas se seleccionan con clic:

    python/.venv/bin/python scripts/demo.py \
      --N 100 --L 20 --M 13 --rc 1 \
      --r-min 0.23 --r-max 0.26 \
      --attempts 100000 --repetitions 100 --boundary walls \
      --output experiments/raw/demo --interactive

`--attempts` limita los intentos de colocación sin superposición. `--repetitions` controla cuántos sistemas independientes se generan y miden, con una semilla aleatoria diferente en cada caso; vale 100 por defecto. Cada semilla queda registrada en `metrics.csv`. La selección con clic afecta únicamente la visualización. La referencia detallada de cada opción está en `../README.md`, sección “Simulación interactiva”.
