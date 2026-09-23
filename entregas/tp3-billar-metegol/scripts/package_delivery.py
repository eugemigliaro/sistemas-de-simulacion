#!/usr/bin/env python3
"""Arma los entregables locales respetando el contrato de TP03, p. 1."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "entrega-final"
STEM = "SdS_TP3_2026Q2G07CS"
CODE_ZIP = DELIVERY / f"{STEM}_Codigo.zip"
CONFIG = ROOT / "experiments/configs" / f"{STEM}_Config.txt"
PRESENTATION = ROOT / "presentacion" / f"{STEM}_Presentacion.pdf"


def main() -> int:
    if not CONFIG.exists() or not PRESENTATION.exists():
        raise FileNotFoundError("faltan la configuración final o la presentación compilada")
    DELIVERY.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CONFIG, DELIVERY / CONFIG.name)
    shutil.copyfile(PRESENTATION, DELIVERY / PRESENTATION.name)

    sources = [ROOT / "cpp/Makefile"]
    sources += sorted((ROOT / "cpp/include/tp3").glob("*.hpp"))
    sources += sorted((ROOT / "cpp/src").glob("*.cpp"))
    with zipfile.ZipFile(CODE_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sources:
            archive.write(source, source.relative_to(ROOT))

    if CODE_ZIP.stat().st_size >= 100_000:
        raise RuntimeError(f"el ZIP supera 100 KB: {CODE_ZIP.stat().st_size} bytes")
    with zipfile.ZipFile(CODE_ZIP) as archive:
        names = archive.namelist()
        if any("test" in name or "build" in name or "python" in name for name in names):
            raise RuntimeError("el ZIP contiene archivos ajenos al motor final")
    print(f"{CODE_ZIP.name}: {CODE_ZIP.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
