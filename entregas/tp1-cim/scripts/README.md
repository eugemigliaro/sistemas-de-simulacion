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
      --output-root experiments/raw/phase8

`demo.py` permite variar parámetros durante la exposición y crea automáticamente la lista y la figura:

    python/.venv/bin/python scripts/demo.py \
      --N 100 --L 20 --M 13 --rc 1 \
      --boundary walls --particle auto --open
