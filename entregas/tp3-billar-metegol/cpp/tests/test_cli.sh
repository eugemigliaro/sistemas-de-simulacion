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

echo "test_cli OK"
