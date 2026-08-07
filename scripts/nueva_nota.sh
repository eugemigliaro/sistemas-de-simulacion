#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 \"tema de la clase\"" >&2
  exit 2
fi

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tema="$*"
fecha="$(date +%F)"
slug="$(printf '%s' "$tema" | iconv -f UTF-8 -t ASCII//TRANSLIT 2>/dev/null | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
[[ -n "$slug" ]] || slug="clase"
destino="$repo_dir/notas/bandeja/${fecha}-${slug}.md"
if [[ -e "$destino" ]]; then
  destino="$repo_dir/notas/bandeja/${fecha}-${slug}-$(date +%H%M%S).md"
fi

python3 - "$repo_dir/notas/PLANTILLA.md" "$destino" "$fecha" "$tema" <<'PY'
from pathlib import Path
import sys

template_path, destination_path, date, topic = sys.argv[1:]
content = Path(template_path).read_text(encoding="utf-8")
content = content.replace("{{FECHA}}", date).replace("{{TEMA}}", topic)
Path(destination_path).write_text(content, encoding="utf-8")
PY
echo "$destino"
