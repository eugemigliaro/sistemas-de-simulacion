#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
catalogo="$repo_dir/material/catalogo.tsv"
salida_dir="$repo_dir/material/extraido"

command -v pdftotext >/dev/null || {
  echo "Falta pdftotext (paquete poppler-utils)." >&2
  exit 1
}
command -v pdfinfo >/dev/null || {
  echo "Falta pdfinfo (paquete poppler-utils)." >&2
  exit 1
}
[[ -f "$catalogo" ]] || {
  echo "Falta material/catalogo.tsv." >&2
  exit 1
}

mkdir -p "$salida_dir"
procesadas=0
while IFS=$'\t' read -r id tipo titulo ruta paginas ciclo estado archivo_original; do
  [[ "$id" == "id" || -z "$id" ]] && continue
  origen="$repo_dir/$ruta"
  [[ "${origen,,}" == *.pdf ]] || continue
  [[ -f "$origen" ]] || {
    echo "No existe la fuente catalogada $id: $ruta" >&2
    exit 1
  }
  total="$(pdfinfo "$origen" | awk -F: '/^Pages:/ {gsub(/[[:space:]]/, "", $2); print $2; exit}')"
  [[ "$total" =~ ^[0-9]+$ ]] || {
    echo "No se pudo determinar la cantidad de páginas de $ruta" >&2
    exit 1
  }
  temporal="$(mktemp "$salida_dir/.${id}.XXXXXX")"
  {
    echo "FUENTE: $id"
    echo "TITULO: $titulo"
    echo "ORIGINAL: $ruta"
    echo "PAGINAS: $total"
    for ((pagina = 1; pagina <= total; pagina++)); do
      printf '\n===== PAGINA %d =====\n\n' "$pagina"
      pdftotext -f "$pagina" -l "$pagina" -layout "$origen" -
    done
  } >"$temporal"
  mv "$temporal" "$salida_dir/$id.txt"
  procesadas=$((procesadas + 1))
done <"$catalogo"

echo "Fuentes PDF extraídas: $procesadas"
