#!/usr/bin/env python3
"""Arma el ZIP de entrega: solo la versión final del motor, sin post-proceso,
pruebas, salidas ni documentación, de unos pocos kB [TP05, p. 1].

Comprueba que el ZIP compile y corra solo, desde una carpeta vacía. El PDF lo
escribe build_presentation.py en la misma carpeta.
"""
import subprocess
import tempfile
import zipfile
from pathlib import Path

from common import ROOT

DELIVERY = ROOT / "entrega-final"
ARCHIVE = DELIVERY / "SdS_TP5_2026Q2G07CS_Codigo.zip"
PRESENTATION = DELIVERY / "SdS_TP5_2026Q2G07CS_Presentación.pdf"
LIMIT = 100 * 1024  # la consigna no fija un máximo; se mantiene el del TP4
# Fecha fija: el mismo código produce el mismo ZIP.
TIMESTAMP = (2026, 11, 16, 0, 0, 0)


def engine_files() -> list[Path]:
    cpp = ROOT / "cpp"
    return [cpp / "Makefile", *sorted((cpp / "include/tp5").glob("*.hpp")), *sorted((cpp / "src").glob("*.cpp"))]


def check_standalone() -> None:
    with tempfile.TemporaryDirectory() as folder:
        with zipfile.ZipFile(ARCHIVE) as archive:
            archive.extractall(folder)
        subprocess.run(["make", "-C", f"{folder}/cpp", "release"], check=True, capture_output=True)
        engine = f"{folder}/cpp/build/release/tp5"
        small = ["--agents", "40", "--side", "10", "--t-max", "5", "--output", f"{folder}/salida.txt"]
        for arguments in (["--help"],
                          ["collision", "--dt", "1e-4", "--speed", "1.5", "--offset", "0.5"],
                          ["evacuate", "--scheme", "tsdmd", "--dt", "2e-3", *small],
                          ["evacuate", "--scheme", "edmd", *small],
                          ["evacuate", "--scheme", "edmd", "--relaxation", "analytic", *small],
                          ["evacuate", "--scheme", "hybrid", "--dt", "2e-3", "--t-star", "0.05", *small]):
            subprocess.run([engine, *arguments], check=True, capture_output=True)


def main() -> None:
    DELIVERY.mkdir(exist_ok=True)
    files = engine_files()
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo(str(path.relative_to(ROOT)), TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    size = ARCHIVE.stat().st_size
    if size >= LIMIT:
        raise SystemExit(f"el ZIP pesa {size} bytes: la consigna pide unos pocos kB")
    check_standalone()
    print(f"{ARCHIVE.relative_to(ROOT)}: {size} bytes, {len(files)} archivos; compila y corre solo")
    if not PRESENTATION.exists():
        print("falta el PDF: correr scripts/build_presentation.py")


if __name__ == "__main__":
    main()
