#!/usr/bin/env python3
"""Verifica invariantes locales del repositorio sin dependencias externas."""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from pathlib import Path

import configurar_materia


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_FIELDS = ["id", "tipo", "titulo", "ruta", "paginas", "ciclo", "estado", "archivo_original"]
CITATION = re.compile(r"\[([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)(?:,\s*p\.\s*\d+)?\]")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_catalog(errors: list[str]) -> set[str]:
    catalog = ROOT / "material/catalogo.tsv"
    if not catalog.is_file():
        errors.append("falta material/catalogo.tsv")
        return set()
    with catalog.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != EXPECTED_FIELDS:
            errors.append("material/catalogo.tsv tiene columnas inesperadas")
            return set()
        rows = list(reader)

    ids: set[str] = set()
    paths: set[str] = set()
    for line, row in enumerate(rows, start=2):
        source_id = row["id"]
        relative = row["ruta"]
        if not source_id:
            errors.append(f"catálogo línea {line}: ID vacío")
        elif source_id in ids:
            errors.append(f"catálogo línea {line}: ID duplicado {source_id}")
        ids.add(source_id)
        if relative in paths:
            errors.append(f"catálogo línea {line}: ruta duplicada {relative}")
        paths.add(relative)
        path = ROOT / relative
        try:
            path.resolve().relative_to(ROOT)
        except ValueError:
            errors.append(f"catálogo línea {line}: ruta fuera del repo {relative}")
        if not path.is_file():
            errors.append(f"catálogo línea {line}: no existe {relative}")
        pages = row["paginas"]
        if pages and not pages.isdigit():
            errors.append(f"catálogo línea {line}: páginas inválidas para {source_id}")
        extracted = ROOT / "material/extraido" / f"{source_id}.txt"
        if extracted.exists() and pages:
            count = extracted.read_text(encoding="utf-8", errors="replace").count("===== PAGINA ")
            if count != int(pages):
                errors.append(f"extracción {source_id}: esperaba {pages} páginas y encontró {count}")
    return ids


def validate_checksums(errors: list[str]) -> None:
    checksum_file = ROOT / "material/checksums.sha256"
    if not checksum_file.is_file():
        errors.append("falta material/checksums.sha256")
        return
    for line_number, line in enumerate(checksum_file.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append(f"checksums línea {line_number}: formato inválido")
            continue
        expected, relative = match.groups()
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"checksums línea {line_number}: no existe {relative}")
        elif sha256(path) != expected:
            errors.append(f"checksum distinto: {relative}")


def validate_citations(ids: set[str], errors: list[str]) -> None:
    for path in (ROOT / "wiki").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for match in CITATION.finditer(text):
            source_id = match.group(1)
            if source_id.startswith("N-"):
                continue
            if source_id not in ids:
                errors.append(f"cita a ID no catalogado {source_id} en {path.relative_to(ROOT)}")


def validate_skills(errors: list[str]) -> None:
    skills_root = ROOT / ".agents/skills"
    skill_files = sorted(skills_root.glob("*/SKILL.md"))
    if not skill_files:
        errors.append("no hay skills en .agents/skills")
    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        if "TODO" in text:
            errors.append(f"skill incompleta: {path.relative_to(ROOT)}")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        if not match:
            errors.append(f"frontmatter inválido: {path.relative_to(ROOT)}")
            continue
        keys = {
            line.partition(":")[0].strip()
            for line in match.group(1).splitlines()
            if ":" in line
        }
        if keys != {"name", "description"}:
            errors.append(f"frontmatter de skill debe tener name y description: {path.relative_to(ROOT)}")


def main() -> int:
    errors = configurar_materia.validate_repo(ROOT)
    ids = validate_catalog(errors)
    validate_checksums(errors)
    validate_citations(ids, errors)
    validate_skills(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repositorio válido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
