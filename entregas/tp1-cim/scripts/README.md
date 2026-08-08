# Automatización

`calibrate_n.py` determina el mayor múltiplo de un paso que el generador puede construir para todas las semillas indicadas, por separado para paredes y periodicidad. Desde la carpeta del TP:

    python/.venv/bin/python scripts/calibrate_n.py \
      --binary cpp/build/release/tp1 \
      --output experiments/configs/phase7-calibration.json \
      --seeds 42 31415 20260807 \
      --attempts 100000 \
      --step 50

La automatización integral de la demostración se incorporará cuando exista `benchmark-n`.
