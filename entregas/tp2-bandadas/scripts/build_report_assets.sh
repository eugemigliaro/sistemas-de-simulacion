#!/usr/bin/env bash
# Genera, desde los CSV crudos, todas las figuras y tablas que usa el informe.
set -euo pipefail

cd "$(dirname "$0")/.."
PY="${PY:-python/.venv/bin/python}"
export PYTHONPATH=python/src
RAW=experiments/raw/production
LOW=experiments/raw/cluster-production
RES=experiments/results
FIG=informe/figuras
T0=4000
mkdir -p "$RES" "$FIG"

run() { "$PY" -m tp2analysis "$@"; }

echo "== 1. Resúmenes estacionarios (t0 = $T0) =="
run summary "$RAW"/*-observables.csv --stationary-start "$T0" --output "$RES/summary-densidades.csv"
run summary "$LOW"/*-observables.csv --stationary-start "$T0" --output "$RES/summary-baja-densidad.csv"

echo "== 2. Bloques que justifican el descarte =="
run blocks "$RAW"/vicsek-rho4-eta0p5-seed[123]-observables.csv \
    --block-size 1000 --start 0 \
    --output "$RES/bloques-vicsek.csv" --plot "$FIG/bloques-vicsek.png"
run blocks "$LOW"/voter-rho0p32-eta0p25-seed[123]-observables.csv \
    --block-size 1000 --start 0 \
    --output "$RES/bloques-votante.csv" --plot "$FIG/bloques-votante.png"

echo "== 3. Series temporales con el inicio del estacionario =="
run timeseries "$RAW"/vicsek-rho4-eta0-seed1-observables.csv \
    "$RAW"/vicsek-rho4-eta0p5-seed1-observables.csv \
    "$RAW"/vicsek-rho4-eta1-seed1-observables.csv \
    --stationary-start "$T0" --output "$FIG/series-vicsek.png"
run timeseries "$RAW"/voter-rho4-eta0-seed1-observables.csv \
    "$RAW"/voter-rho4-eta0p05-seed1-observables.csv \
    "$RAW"/voter-rho4-eta0p25-seed1-observables.csv \
    --stationary-start "$T0" --output "$FIG/series-votante.png"
run timeseries "$LOW"/vicsek-rho0p32-eta0p25-seed1-observables.csv \
    "$LOW"/vicsek-rho0p16-eta0p25-seed1-observables.csv \
    "$LOW"/vicsek-rho0p11-eta0p25-seed1-observables.csv \
    --stationary-start "$T0" --output "$FIG/series-baja-densidad.png"

echo "== 4. Observable escalar contra el ruido =="
run plot-eta --input "$RES/summary-densidades.csv"   --observable polarization --output "$FIG/va-vs-eta.png"
run plot-eta --input "$RES/summary-densidades.csv"   --observable cluster      --output "$FIG/s-vs-eta.png"
run plot-eta --input "$RES/summary-baja-densidad.csv" --observable cluster     --output "$FIG/s-vs-eta-baja-densidad.png"
run plot-eta --input "$RES/summary-baja-densidad.csv" --observable polarization --output "$FIG/va-vs-eta-baja-densidad.png"

echo "== 5. Polarización contra componente gigante =="
run plot-va-s --input "$RES/summary-densidades.csv"   --output "$FIG/va-vs-s.png"
run plot-va-s --input "$RES/summary-baja-densidad.csv" --invert-axes \
    --output "$FIG/va-vs-s-baja-densidad.png"

echo "== 6. Tiempos del CIM y comparación con el TP1 =="
run cim-summary "$RAW"/*-observables.csv --start "$T0" --output "$RES/cim-summary.csv"
run plot-cim --input "$RES/cim-summary.csv" \
    --tp1 ../tp1-cim/experiments/results/summary-n-periodic.csv \
    --output "$FIG/cim-comparacion.png"

echo "== Listo. Figuras en $FIG, tablas en $RES =="
