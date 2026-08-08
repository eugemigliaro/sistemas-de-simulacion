#!/bin/sh
set -eu

binary=$1
temporary_directory=$(mktemp -d "${TMPDIR:-/tmp}/tp1-cli.XXXXXX")
trap 'rm -rf "$temporary_directory"' EXIT HUP INT TERM

static_walls="$temporary_directory/static-walls.txt"
dynamic_walls="$temporary_directory/dynamic-walls.txt"
brute_walls="$temporary_directory/brute-walls.txt"
cim_walls="$temporary_directory/cim-walls.txt"
metrics="$temporary_directory/metrics.csv"
metrics_n="$temporary_directory/metrics-n.csv"

"$binary" generate \
    --N 100 --L 20 --seed 42 --boundary walls \
    --static "$static_walls" --dynamic "$dynamic_walls" >/dev/null

"$binary" neighbors \
    --method brute-force \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --rc 1 --boundary walls --output "$brute_walls" >/dev/null

"$binary" neighbors \
    --method cim --M 10 \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --rc 1 --boundary walls --output "$cim_walls" >/dev/null

cmp "$brute_walls" "$cim_walls"

static_periodic="$temporary_directory/static-periodic.txt"
dynamic_periodic="$temporary_directory/dynamic-periodic.txt"
brute_periodic="$temporary_directory/brute-periodic.txt"
cim_periodic="$temporary_directory/cim-periodic.txt"

"$binary" generate \
    --N 100 --L 20 --seed 42 --boundary periodic \
    --static "$static_periodic" --dynamic "$dynamic_periodic" >/dev/null

"$binary" neighbors \
    --method brute-force \
    --static "$static_periodic" --dynamic "$dynamic_periodic" \
    --rc 1 --boundary periodic --output "$brute_periodic" >/dev/null

"$binary" neighbors \
    --method cim --M 10 \
    --static "$static_periodic" --dynamic "$dynamic_periodic" \
    --rc 1 --boundary periodic --output "$cim_periodic" >/dev/null

cmp "$brute_periodic" "$cim_periodic"

"$binary" benchmark-m \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --rc 1 --boundary walls --seed 42 --repetitions 2 \
    --output "$metrics" >/dev/null

expected_header='seed,boundary,method,N,L,M,rc,repetition,time_ns,neighbor_pairs,distance_evaluations'
actual_header=$(sed -n '1p' "$metrics")
test "$actual_header" = "$expected_header"
test "$(wc -l < "$metrics" | tr -d ' ')" -eq 27

awk -F, '
    NR == 1 { next }
    $6 == 1 && $3 != "brute_force" { exit 1 }
    $6 > 1 && $3 != "cim" { exit 1 }
    $8 < 1 || $8 > 2 { exit 1 }
    $9 < 0 { exit 1 }
    END { if (NR != 27) exit 1 }
' "$metrics"

"$binary" benchmark-n \
    --M 10 --static "$static_walls" --dynamic "$dynamic_walls" \
    --rc 1 --boundary walls --seed 42 --repetitions 2 \
    --output "$metrics_n" >/dev/null

test "$(sed -n '1p' "$metrics_n")" = "$expected_header"
test "$(wc -l < "$metrics_n" | tr -d ' ')" -eq 3
awk -F, '
    NR == 1 { next }
    $3 != "cim" || $4 != 100 || $6 != 10 { exit 1 }
    $8 < 1 || $8 > 2 { exit 1 }
    END { if (NR != 3) exit 1 }
' "$metrics_n"

if "$binary" neighbors \
    --method cim \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --output "$temporary_directory/missing-m.txt" >/dev/null 2>&1; then
    exit 1
fi

if "$binary" neighbors \
    --method brute-force --M 2 \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --output "$temporary_directory/unused-m.txt" >/dev/null 2>&1; then
    exit 1
fi

if "$binary" neighbors \
    --method cim --M 14 \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --output "$temporary_directory/invalid-m.txt" >/dev/null 2>&1; then
    exit 1
fi

if "$binary" neighbors \
    --method cim --M 0 \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --output "$temporary_directory/zero-m.txt" >/dev/null 2>&1; then
    exit 1
fi

if "$binary" neighbors \
    --method unknown \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --output "$temporary_directory/unknown-method.txt" >/dev/null 2>&1; then
    exit 1
fi

if "$binary" benchmark-m \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --seed 42 --output "$temporary_directory/missing-repetitions.csv" \
    >/dev/null 2>&1; then
    exit 1
fi

if "$binary" benchmark-n \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --seed 42 --repetitions 2 \
    --output "$temporary_directory/missing-n-m.csv" \
    >/dev/null 2>&1; then
    exit 1
fi

if "$binary" benchmark-n \
    --M 14 --static "$static_walls" --dynamic "$dynamic_walls" \
    --seed 42 --repetitions 2 \
    --output "$temporary_directory/invalid-n-m.csv" \
    >/dev/null 2>&1; then
    exit 1
fi

if "$binary" benchmark-m \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --repetitions 2 --output "$temporary_directory/missing-seed.csv" \
    >/dev/null 2>&1; then
    exit 1
fi

if "$binary" benchmark-m \
    --static "$static_walls" --dynamic "$dynamic_walls" \
    --seed 42 --repetitions 0 \
    --output "$temporary_directory/zero-repetitions.csv" \
    >/dev/null 2>&1; then
    exit 1
fi

echo "CLI integration tests OK"
