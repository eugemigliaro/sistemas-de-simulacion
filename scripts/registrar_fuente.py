#!/usr/bin/env python3
"""Registra una fuente sin sobrescribir originales ni perder trazabilidad."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
CATALOG_FIELDS = ("id", "tipo", "titulo", "ruta", "paginas", "ciclo", "estado", "archivo_original")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pdf_pages(path: Path) -> str:
    if path.suffix.lower() != ".pdf" or shutil.which("pdfinfo") is None:
        return ""
    result = subprocess.run(
        ["pdfinfo", str(path)], capture_output=True, text=True, check=False
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return line.partition(":")[2].strip()
    return ""


def read_catalog(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def destination_for(args: argparse.Namespace, source: Path, root: Path) -> Path:
    if args.destino:
        relative = Path(args.destino)
    elif args.coleccion == "externo":
        relative = Path("material/externo") / source.name
    else:
        relative = Path("material/catedra") / args.seccion / source.name
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("el destino debe ser una ruta relativa segura")
    destination = (root / relative).resolve()
    try:
        destination.relative_to(root)
    except ValueError as error:
        raise ValueError("el destino queda fuera del repositorio") from error
    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archivo", type=Path)
    parser.add_argument("--id", required=True, help="ID estable, por ejemplo T01 o P02")
    parser.add_argument("--tipo", required=True, help="tipo humano: teoria, practica, guia, bibliografia...")
    parser.add_argument("--titulo", required=True)
    parser.add_argument("--coleccion", choices=("catedra", "externo"), default="catedra")
    parser.add_argument("--seccion", choices=("teoria", "practica"), default="teoria")
    parser.add_argument("--destino", help="ruta relativa explícita dentro del repo")
    parser.add_argument("--ciclo", default="")
    parser.add_argument("--estado", default="vigente")
    parser.add_argument("--mover", action="store_true", help="mueve en lugar de copiar el archivo")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()
    source = args.archivo.resolve()
    if not source.is_file():
        parser.error(f"no existe el archivo: {source}")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", args.id):
        parser.error("--id solo admite letras, números y guiones, y debe comenzar con letra")
    metadata = (args.tipo, args.titulo, args.ciclo, args.estado, source.name)
    if any("\t" in value or "\n" in value or "\r" in value for value in metadata):
        parser.error("los metadatos y el nombre de archivo no pueden contener tabs ni saltos de línea")

    catalog_path = root / "material/catalogo.tsv"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    rows = read_catalog(catalog_path)
    normalized_id = args.id.upper()
    if any(row.get("id") == normalized_id for row in rows):
        parser.error(f"el ID {normalized_id} ya está registrado")

    try:
        destination = destination_for(args, source, root)
    except ValueError as error:
        parser.error(str(error))
    relative = destination.relative_to(root).as_posix()
    if destination.exists():
        parser.error(f"el destino ya existe: {relative}")
    if any(row.get("ruta") == relative for row in rows):
        parser.error(f"la ruta ya está registrada: {relative}")

    original_hash = sha256(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if args.mover:
        shutil.move(str(source), destination)
    else:
        shutil.copy2(source, destination)
    if sha256(destination) != original_hash:
        destination.unlink(missing_ok=True)
        raise RuntimeError("la copia no conserva el contenido original")

    row = {
        "id": normalized_id,
        "tipo": args.tipo,
        "titulo": args.titulo,
        "ruta": relative,
        "paginas": pdf_pages(destination),
        "ciclo": args.ciclo,
        "estado": args.estado,
        "archivo_original": source.name,
    }
    catalog_exists = catalog_path.exists() and catalog_path.stat().st_size > 0
    with catalog_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CATALOG_FIELDS, delimiter="\t", lineterminator="\n")
        if not catalog_exists:
            writer.writeheader()
        writer.writerow(row)

    if args.coleccion == "catedra":
        with (root / "material/checksums.sha256").open("a", encoding="utf-8") as handle:
            handle.write(f"{original_hash}  {relative}\n")
    print(f"Registrada {normalized_id}: {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
