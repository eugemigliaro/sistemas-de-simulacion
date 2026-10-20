"""Arma el ZIP de entrega solo con el motor final [TP04, p. 1].

El ZIP no lleva post-proceso, pruebas, harness de benchmark, salidas ni
documentación. Se verifica que compile y corra solo, desde una carpeta vacía.
El PDF lo escribe build_presentation.py en la misma carpeta; acá solo se
comprueba que esté.
"""
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEM = "SdS_TP4_2026Q2G07CS"
DELIVERY = ROOT / "entrega-final"
CODE_ZIP = DELIVERY / f"{STEM}_Codigo.zip"
PRESENTATION = DELIVERY / f"{STEM}_Presentación.pdf"
FILES = ["cpp/Makefile", "cpp/src/main.cpp", *sorted(
    str(p.relative_to(ROOT)) for p in (ROOT / "cpp/include/tp4").glob("*.hpp"))]
LIMIT_BYTES = 100 * 1024
# Fecha fija: el mismo código produce el mismo ZIP.
TIMESTAMP = (2026, 10, 23, 0, 0, 0)


def check_standalone(archive):
    with tempfile.TemporaryDirectory() as folder:
        with zipfile.ZipFile(archive) as z:
            z.extractall(folder)
        subprocess.run(["make", "-C", f"{folder}/cpp", "release"], check=True, capture_output=True, text=True)
        engine = f"{folder}/cpp/build/release/tp4"
        runs = [["--help"],
                ["oscillator", "--method", "beeman", "--steps", "100", "--output", f"{folder}/osc.csv"],
                ["billiard", "--n", "20", "--duration", ".01", "--obstacles", "1", "--output", f"{folder}/random.csv"],
                ["billiard", "--n", "650", "--duration", ".0025", "--save-every", "200", "--obstacles", "1",
                 "--initialization", "dense", "--sweeps", "5", "--output", f"{folder}/dense.csv"]]
        for arguments in runs:
            subprocess.run([engine, *arguments], check=True, capture_output=True, text=True)


def main():
    DELIVERY.mkdir(exist_ok=True)
    with zipfile.ZipFile(CODE_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for name in FILES:
            info = zipfile.ZipInfo(name, TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, (ROOT / name).read_bytes())
    size = CODE_ZIP.stat().st_size
    if size >= LIMIT_BYTES:
        raise RuntimeError(f"ZIP de {size} bytes: la consigna exige menos de 100 KB")
    check_standalone(CODE_ZIP)
    print(f"{CODE_ZIP.relative_to(ROOT)}: {size} bytes, {len(FILES)} archivos; compila y corre solo.")
    if not PRESENTATION.exists():
        raise RuntimeError("Falta el PDF: correr python/build_presentation.py")
    print(f"{PRESENTATION.relative_to(ROOT)} presente.")


if __name__ == "__main__":
    main()
