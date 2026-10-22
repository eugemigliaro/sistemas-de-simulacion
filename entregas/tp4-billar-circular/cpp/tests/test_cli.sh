#!/bin/sh
# Pruebas de la línea de comandos: códigos de salida y forma de la salida.
set -u
binary=$1
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
failures=0

expect_status() {
    expected=$1
    shift
    "$binary" "$@" >"$work/out" 2>"$work/err"
    status=$?
    if [ "$status" -ne "$expected" ]; then
        echo "cli: se esperaba salida $expected y fue $status: $*" >&2
        failures=$((failures + 1))
    fi
}

expect_status 0 --help
expect_status 2
expect_status 2 billiard --n 10 --dt 1e-4
expect_status 2 billiard --n 10 --dt 1e-4 --tf 0.01 --colour red
expect_status 2 billiard --n 10 --dt 1e-4 --tf 0.01 --n 20
expect_status 2 billiard --n 10 --dt 3e-3 --tf 0.01
expect_status 2 billiard --n 10 --dt 1e-4 --tf 0.01 --output-every 3
expect_status 2 billiard --n 10 --dt 1e-4 --tf 0.01 --x0 0.6
expect_status 2 billiard --n -1 --dt 1e-4 --tf 0.01
expect_status 2 oscillator --integrator rk4 --dt 1e-3
expect_status 1 billiard --n 650 --dt 1e-4 --tf 0.01 --x0 0.0175
expect_status 1 billiard --n 10 --dt 1e-4 --tf 0.01 --output "$work/no/existe.txt"

expect_status 0 billiard --n 10 --dt 1e-4 --tf 0.01 --output-every 20 --x0 0.0175 --seed 3 --output "$work/b.txt"
frames=$(grep -c '^frame ' "$work/b.txt")
states=$(grep -c -v -e '^frame ' -e '^#' "$work/b.txt")
if [ "$frames" -ne 6 ] || [ "$states" -ne 60 ]; then
    echo "cli: el billar escribio $frames cuadros y $states estados" >&2
    failures=$((failures + 1))
fi

expect_status 0 billiard --n 650 --dt 1e-4 --tf 0.001 --x0 0.0175 --layout lattice --sweeps 5 --output "$work/d.txt"

expect_status 0 oscillator --integrator verlet --dt 0.01 --output "$work/o.txt"
samples=$(grep -c -v '^#' "$work/o.txt")
if [ "$samples" -ne 501 ]; then
    echo "cli: el oscilador escribio $samples muestras" >&2
    failures=$((failures + 1))
fi

if [ "$failures" -ne 0 ]; then
    echo "cli: $failures fallas" >&2
    exit 1
fi
echo "cli: OK"
