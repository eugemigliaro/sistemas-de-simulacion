#!/bin/sh
set -eu

binary="$1"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

"$binary" --help | grep -q 'tp2 simulate'
"$binary" --version | grep -q '^0.1.0$'

"$binary" simulate \
    --model voter \
    --rho 0.04 \
    --eta 0 \
    --steps 2 \
    --seed 5 \
    --M 9 \
    --trajectory-every 2 \
    --trajectory "$tmp_dir/trajectory.csv" \
    --observables "$tmp_dir/observables.csv" >/dev/null

test "$(wc -l < "$tmp_dir/trajectory.csv")" -eq 9
test "$(wc -l < "$tmp_dir/observables.csv")" -eq 4
grep -q '^voter,' "$tmp_dir/trajectory.csv"
grep -q '^voter,' "$tmp_dir/observables.csv"

"$binary" simulate \
    --model vicsek \
    --rho 0.04 \
    --eta 0 \
    --steps 2 \
    --seed 6 \
    --M 9 \
    --observables "$tmp_dir/observables-only.csv" >/dev/null
test "$(wc -l < "$tmp_dir/observables-only.csv")" -eq 4

if "$binary" simulate \
    --model vicsek --rho 2 --eta 1.1 --steps 1 --seed 1 \
    --trajectory "$tmp_dir/bad-t.csv" \
    --observables "$tmp_dir/bad-o.csv" >/dev/null 2>&1; then
    echo "eta inválido fue aceptado" >&2
    exit 1
fi

echo "CLI tests OK"
