#!/usr/bin/env python3
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Empaqueta únicamente el motor C++ final solicitado por la consigna."
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def source_files(root: Path) -> list[Path]:
    cpp = root / "cpp"
    files = [cpp / "Makefile"]
    files.extend(sorted((cpp / "include").rglob("*.hpp")))
    files.extend(sorted((cpp / "src").glob("*.cpp")))
    if any(not path.is_file() for path in files):
        raise ValueError("faltan archivos del motor")
    return files


def main() -> int:
    arguments = parse_args()
    if arguments.output.suffix.lower() != ".zip":
        raise ValueError("el archivo de salida debe terminar en .zip")
    if arguments.output.exists() and not arguments.force:
        raise ValueError("el ZIP ya existe; use --force para reemplazarlo")
    root = Path(__file__).resolve().parents[1]
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        arguments.output,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for source in source_files(root):
            archive.write(source, source.relative_to(root))
    print(f"Código empaquetado en {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
