#!/usr/bin/env python3
"""Configura el template o agrega su contrato mínimo a un repo existente."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
from pathlib import Path


TEMPLATE_VERSION = "0.1.0"
DEFAULT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRS = (
    "wiki/temas",
    "wiki/repaso",
    "material/catedra/teoria",
    "material/catedra/practica",
    "material/entrada",
    "material/externo",
    "material/extraido",
    "material/figuras",
    "notas/bandeja",
    "notas/procesadas",
    "practica",
    "entregas",
    "laboratorio",
)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug or "materia"


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_config(args: argparse.Namespace) -> str:
    slug = args.slug or slugify(args.nombre)
    return f'''schema_version: 1
template_version: {yaml_string(TEMPLATE_VERSION)}
configurada: true

materia:
  nombre: {yaml_string(args.nombre)}
  slug: {yaml_string(slug)}
  institucion: {yaml_string(args.institucion)}
  carrera: {yaml_string(args.carrera)}
  ciclo: {yaml_string(args.ciclo)}
  idioma: {yaml_string(args.idioma)}

estudio:
  modo: {yaml_string(args.modo)}
  citar_paginas: true

practica:
  guias_son_entregables: {str(args.guias_entregables).lower()}
  trabajo_grupal_activo: {str(args.trabajo_grupal_activo).lower()}

laboratorio:
  herramienta: {yaml_string(args.herramienta)}
  dialecto_o_runtime: {yaml_string(args.dialecto)}

fuentes:
  prioridad: ["catedra", "notas", "externo", "conocimiento_general"]
'''


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def update_readme_title(readme: Path, title: str) -> bool:
    if not readme.exists():
        return False
    content = readme.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(<!-- course-title:start -->\s*\n).*?(\n<!-- course-title:end -->)",
        re.DOTALL,
    )
    updated, count = pattern.subn(
        lambda match: f"{match.group(1)}# {title}{match.group(2)}", content, count=1
    )
    if count:
        atomic_write(readme, updated)
    return bool(count)


def validate_repo(root: Path) -> list[str]:
    errors: list[str] = []
    config = root / "materia.yaml"
    if not config.is_file():
        return ["falta materia.yaml"]
    text = config.read_text(encoding="utf-8")
    checks = {
        "schema_version": r"(?m)^schema_version:\s*1\s*$",
        "template_version": r"(?m)^template_version:\s*[\"']?[^\s\"']+[\"']?\s*$",
        "configurada": r"(?m)^configurada:\s*(?:true|false)\s*$",
        "materia.nombre": r"(?m)^\s{2}nombre:\s*.+$",
        "estudio.modo": r"(?m)^\s{2}modo:\s*[\"']?(?:adaptativo|pistas|directo)[\"']?\s*$",
        "laboratorio.herramienta": r"(?m)^\s{2}herramienta:\s*.+$",
    }
    for label, pattern in checks.items():
        if not re.search(pattern, text):
            errors.append(f"materia.yaml no declara correctamente {label}")
    version_file = root / ".course-wiki-version"
    if not version_file.is_file() or not version_file.read_text(encoding="utf-8").strip():
        errors.append("falta .course-wiki-version")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nombre", help="nombre humano de la materia")
    parser.add_argument("--slug", help="identificador corto; se deriva del nombre si se omite")
    parser.add_argument("--institucion", default="")
    parser.add_argument("--carrera", default="")
    parser.add_argument("--ciclo", default="")
    parser.add_argument("--idioma", default="es")
    parser.add_argument("--modo", choices=("adaptativo", "pistas", "directo"), default="adaptativo")
    parser.add_argument("--herramienta", default="ninguna")
    parser.add_argument("--dialecto", default="")
    parser.add_argument("--guias-entregables", action="store_true")
    parser.add_argument("--trabajo-grupal-activo", action="store_true")
    parser.add_argument("--adoptar", action="store_true", help="no crea directorios ni cambia README")
    parser.add_argument("--sin-readme", action="store_true")
    parser.add_argument("--force", action="store_true", help="reemplaza una configuración existente")
    parser.add_argument("--validate", action="store_true", help="solo valida el contrato mínimo")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.validate:
        errors = validate_repo(root)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("materia.yaml: OK")
        return 0
    if not args.nombre:
        parser.error("--nombre es obligatorio salvo con --validate")

    config = root / "materia.yaml"
    if config.exists() and re.search(r"(?m)^configurada:\s*true\s*$", config.read_text(encoding="utf-8")) and not args.force:
        parser.error("la materia ya está configurada; usá --force para reemplazarla")

    root.mkdir(parents=True, exist_ok=True)
    if not args.adoptar:
        for relative in REQUIRED_DIRS:
            (root / relative).mkdir(parents=True, exist_ok=True)
    atomic_write(config, render_config(args))
    atomic_write(root / ".course-wiki-version", f"{TEMPLATE_VERSION}\n")
    if not args.adoptar and not args.sin_readme:
        update_readme_title(root / "README.md", args.nombre)
    print(f"Materia configurada: {args.nombre} ({args.slug or slugify(args.nombre)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
