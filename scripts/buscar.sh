#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 término [opciones de rg]" >&2
  exit 2
fi
command -v rg >/dev/null || {
  echo "Falta ripgrep (rg)." >&2
  exit 1
}

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
consulta="$*"
rg -n -i --glob '!material/catedra/**' --glob '!*.pdf' -- "$consulta" \
  "$repo_dir/wiki" "$repo_dir/material/extraido" "$repo_dir/notas" \
  "$repo_dir/practica" "$repo_dir/entregas" "$repo_dir/laboratorio"
