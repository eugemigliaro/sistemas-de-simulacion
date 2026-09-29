#!/usr/bin/env bash
# Competencia del TP3 [TP03, p. 3]: corre la configuración entregada con
# semillas aleatorias y muestra t90 de cada realización.
#
#   scripts/competencia.sh        una realización
#   scripts/competencia.sh 5      cinco realizaciones y su <t90>
#
# Parámetros fijos de la competencia: N = 100, tmax = 100 s y posiciones
# iniciales al azar en toda el área disponible. Cada ejecución guarda sus
# trayectorias en su propia carpeta dentro de competencia/, así nada se pisa.
set -euo pipefail
cd "$(dirname "$0")/.."

CANTIDAD="${1:-1}"
MOTOR=cpp/build/release/tp3
CONFIG=entrega-final/SdS_TP3_2026Q2G07CS_Config.txt
PY=python/.venv/bin/python

[ -x "$MOTOR" ] || make -C cpp release >/dev/null
DIR="competencia/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DIR"

for ((i = 1; i <= CANTIDAD; i++)); do
  SEMILLA=$(od -An -N4 -tu4 /dev/urandom | tr -d ' ')
  "$MOTOR" simulate --n 100 --seed "$SEMILLA" --tmax 100 --config "$CONFIG" \
    --output "$DIR/semilla_$SEMILLA.txt" 2> "$DIR/semilla_$SEMILLA.log"
  PYTHONPATH=python/src "$PY" - "$DIR/semilla_$SEMILLA.txt" <<'EOF'
import sys
from tp3analysis.goals import time_to_fraction
from tp3analysis.trajectory import read_trajectory

r = time_to_fraction(read_trajectory(sys.argv[1]))
# t90 con todas las cifras que escribió el motor, sin redondear.
t90 = "no llegó al 90 %" if r.t90 is None else f"{r.t90!r} s"
print(f"semilla {r.seed}: t90 = {t90}  (goles al final: {r.goals_at_end})")
EOF
done

if (( CANTIDAD > 1 )); then
  echo "---"
  # El análisis escribe t90.csv y su resumen; el promedio en pantalla se
  # calcula acá con más decimales.
  PYTHONPATH=python/src "$PY" -m tp3analysis t90 "$DIR"/semilla_*.txt \
    --output "$DIR/t90.csv" > "$DIR/resumen.txt"
  PYTHONPATH=python/src "$PY" - "$DIR"/semilla_*.txt <<'PROMEDIO' | tee -a "$DIR/resumen.txt"
import math
import statistics
import sys
from tp3analysis.goals import time_to_fraction
from tp3analysis.trajectory import read_trajectory

resultados = [time_to_fraction(read_trajectory(ruta)) for ruta in sys.argv[1:]]
t90 = [r.t90 for r in resultados if r.t90 is not None]
print(f"realizaciones {len(resultados)}, llegaron al 90 %: {len(t90)}")
if t90:
    media = statistics.fmean(t90)
    desvio = statistics.stdev(t90) if len(t90) > 1 else float("nan")
    print(f"<t90> = {media:.7f} s  desvío = {desvio:.7f} s  "
          f"error estándar = {desvio / math.sqrt(len(t90)):.7f} s")
goles = statistics.fmean(r.goals_at_end for r in resultados)
print(f"<goles al final> = {goles:.2f}")
PROMEDIO
fi
echo "trayectorias en $DIR"
