#!/bin/sh
# Prueba de la interfaz de linea de comandos del motor.
set -eu

binary="$1"
workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

fail() {
    echo "test_cli: $1" >&2
    exit 1
}

# --version
"$binary" --version | grep -q "tp3-billar-metegol" || fail "--version no imprime el nombre"

# Sin argumentos: uso por stderr y codigo 1.
if "$binary" >/dev/null 2>&1; then
    fail "sin argumentos deberia fallar"
fi

# Comando desconocido.
if "$binary" inexistente >/dev/null 2>&1; then
    fail "un comando desconocido deberia fallar"
fi

# generate requiere --n.
if "$binary" generate >/dev/null 2>&1; then
    fail "generate sin --n deberia fallar"
fi

# Mesa vacia.
"$binary" generate --n 10 --seed 1 --output "$workdir/empty.txt"
grep -q "^# tp3-trajectory 1$" "$workdir/empty.txt" || fail "falta la cabecera"
grep -q "^# particle_count 10$" "$workdir/empty.txt" || fail "falta particle_count"
grep -q "^# obstacle_count 0$" "$workdir/empty.txt" || fail "falta obstacle_count"
grep -q "^frame 0 0 0 initial$" "$workdir/empty.txt" || fail "falta el cuadro inicial"
lines="$(grep -c -v '^#' "$workdir/empty.txt")"
[ "$lines" -eq 11 ] || fail "se esperaban 11 lineas sin comentario, hay $lines"

# Misma semilla, mismo archivo.
"$binary" generate --n 10 --seed 1 --output "$workdir/empty2.txt"
cmp -s "$workdir/empty.txt" "$workdir/empty2.txt" || fail "la misma semilla no reproduce"

# Semilla distinta, archivo distinto.
"$binary" generate --n 10 --seed 2 --output "$workdir/other.txt"
if cmp -s "$workdir/empty.txt" "$workdir/other.txt"; then
    fail "semillas distintas producen el mismo archivo"
fi

# Con obstaculos leidos de archivo.
printf '0.30 0.34 0.05\n0.90 0.34 0.05\n' > "$workdir/config.txt"
"$binary" generate --n 20 --seed 3 --config "$workdir/config.txt" --output "$workdir/with.txt"
grep -q "^# obstacle_count 2$" "$workdir/with.txt" || fail "no se leyeron los obstaculos"
grep -q "^# obstacle 0.3 0.34 0.05$" "$workdir/with.txt" || fail "obstaculo mal escrito"

# Configuracion inexistente.
if "$binary" generate --n 5 --config "$workdir/no-existe.txt" >/dev/null 2>&1; then
    fail "una configuracion inexistente deberia fallar"
fi

# Obstaculo invalido (Rk < r).
printf '0.60 0.34 0.001\n' > "$workdir/bad.txt"
if "$binary" generate --n 5 --config "$workdir/bad.txt" >/dev/null 2>&1; then
    fail "un obstaculo con Rk < r deberia fallar"
fi

# Configuracion que no permite generar las N particulas.
if "$binary" generate --n 2000 --max-attempts 200 >/dev/null 2>&1; then
    fail "una configuracion imposible deberia fallar"
fi

# --- simulate ---------------------------------------------------------------

# simulate requiere --tmax.
if "$binary" simulate --n 10 >/dev/null 2>&1; then
    fail "simulate sin --tmax deberia fallar"
fi

# Las opciones de simulate no valen para generate.
if "$binary" generate --n 10 --tmax 1 >/dev/null 2>&1; then
    fail "generate deberia rechazar --tmax"
fi

# Motor desconocido.
if "$binary" simulate --n 10 --tmax 1 --engine inexistente >/dev/null 2>&1; then
    fail "un motor desconocido deberia fallar"
fi

# Corrida corta sobre la mesa vacia.
"$binary" simulate --n 15 --seed 4 --tmax 2 --save-every 20 \
    --output "$workdir/run.txt" 2>"$workdir/run.err"
grep -q "^# save_every 20$" "$workdir/run.txt" || fail "falta save_every en la cabecera"
grep -q "^frame 0 0 0 initial$" "$workdir/run.txt" || fail "falta el cuadro inicial"
grep -q " final$" "$workdir/run.txt" || fail "falta el cuadro final"
grep -q "^engine queue particles 15 seed 4 events " "$workdir/run.err" \
    || fail "falta el resumen por stderr"

# El cuadro final cierra en tmax y los cuadros no retroceden en el tiempo.
grep '^frame ' "$workdir/run.txt" | tail -1 | grep -q ' 2 .* final$' \
    || fail "el cuadro final no esta en tmax"
grep '^frame ' "$workdir/run.txt" | awk '
    NR > 1 && $3 < previous { exit 1 }
    { previous = $3 }
' || fail "los cuadros no estan ordenados en el tiempo"

# Cada cuadro trae una linea por particula.
frames="$(grep -c '^frame ' "$workdir/run.txt")"
rows="$(grep -c -v -e '^#' -e '^frame ' "$workdir/run.txt")"
[ "$rows" -eq $((frames * 15)) ] || fail "faltan filas de particulas"

# El estado solo puede ser 0 o 1.
if grep -v -e '^#' -e '^frame ' "$workdir/run.txt" | awk '$5 != 0 && $5 != 1' | grep -q .; then
    fail "hay estados distintos de 0 y 1"
fi

# Misma semilla, misma corrida.
"$binary" simulate --n 15 --seed 4 --tmax 2 --save-every 20 \
    --output "$workdir/run2.txt" 2>/dev/null
cmp -s "$workdir/run.txt" "$workdir/run2.txt" || fail "la misma semilla no reproduce la corrida"

# El motor por defecto es el de cola.
"$binary" simulate --n 10 --seed 4 --tmax 1 --output /dev/null 2>"$workdir/default.err"
grep -q "^engine queue " "$workdir/default.err" || fail "el motor por defecto deberia ser queue"

# Los dos motores corren y conservan el formato.
for engine in naive queue; do
    "$binary" simulate --engine "$engine" --n 20 --seed 6 --tmax 3 \
        --output "$workdir/$engine.txt" 2>"$workdir/$engine.err"
    grep -q "^engine $engine particles 20 " "$workdir/$engine.err" \
        || fail "$engine no reporta su nombre"
    grep -q " final$" "$workdir/$engine.txt" || fail "$engine no cierra con el cuadro final"
done

# Con pocos eventos los dos motores dan el mismo estado: la divergencia por
# redondeo todavia es despreciable.
"$binary" simulate --engine naive --n 20 --seed 6 --tmax 1000 --max-events 1 \
    --output "$workdir/one-naive.txt" 2>/dev/null
"$binary" simulate --engine queue --n 20 --seed 6 --tmax 1000 --max-events 1 \
    --output "$workdir/one-queue.txt" 2>/dev/null
cmp -s "$workdir/one-naive.txt" "$workdir/one-queue.txt" \
    || fail "los motores difieren ya en el primer evento"

# El tope de eventos corta antes de tmax.
"$binary" simulate --n 15 --seed 4 --tmax 1000 --max-events 5 \
    --output "$workdir/capped.txt" 2>"$workdir/capped.err"
grep -q " events 5 " "$workdir/capped.err" || fail "--max-events no corto la corrida"

echo "test_cli OK"
