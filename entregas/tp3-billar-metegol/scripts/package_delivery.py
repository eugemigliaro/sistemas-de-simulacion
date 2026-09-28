#!/usr/bin/env python3
"""Arma los entregables locales respetando el contrato de TP03, p. 1.

El ZIP lleva el motor final y, por pedido de la cátedra, el código que genera
las animaciones, para que se pueda verificar que no interpolan entre eventos.
El resto del posprocesamiento (DCM, ajustes, estadística) queda afuera.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "entrega-final"
STEM = "SdS_TP3_2026Q2G07CS"
CODE_ZIP = DELIVERY / f"{STEM}_Codigo.zip"
CONFIG = ROOT / "experiments/configs" / f"{STEM}_Config.txt"
PRESENTATION = ROOT / "presentacion" / f"{STEM}_Presentacion.pdf"
# La consigna nombra el entregable con tilde [TP03, p. 1]; la fuente queda sin
# tilde para no depender del manejo de nombres Unicode de las herramientas.
DELIVERED_PRESENTATION = DELIVERY / f"{STEM}_Presentación.pdf"
# El motor ingenuo queda en el repositorio como oráculo de los tests, pero el
# ZIP incluye únicamente la versión final del motor [TP03, p. 1].
NAIVE_FILES = {"cpp/src/naive.cpp", "cpp/include/tp3/naive.hpp"}
# Animación: el punto de entrada y solo los módulos que usa.
ANIMATION_FILES = [
    "python/requirements.txt",
    "python/src/tp3analysis/__init__.py",
    "python/src/tp3analysis/trajectory.py",
    "python/src/tp3analysis/goals.py",
    "python/src/tp3analysis/animation.py",
    "python/src/tp3analysis/animar.py",
]
PYTHON = ROOT / "python/.venv/bin/python"
NAIVE_MAKE_BLOCK = """# El motor ingenuo (oraculo de los tests) solo se compila si esta su fuente:
# el ZIP de entrega no la incluye [TP03, p. 1].
ifneq ($(wildcard src/naive.cpp),)
CPPFLAGS += -DTP3_WITH_NAIVE
endif
"""


def without_naive(relative: str, text: str) -> str:
    """Quita los bloques condicionales del motor ingenuo, conservando los #else."""
    if relative == "cpp/Makefile":
        if NAIVE_MAKE_BLOCK not in text:
            raise RuntimeError("cambió el bloque del motor ingenuo en el Makefile")
        return text.replace(NAIVE_MAKE_BLOCK, "")
    kept, state = [], "fuera"
    for line in text.splitlines(keepends=True):
        directive = line.strip()
        if directive == "#ifdef TP3_WITH_NAIVE":
            if state != "fuera":
                raise RuntimeError(f"{relative}: bloques anidados del motor ingenuo")
            state = "adentro"
        elif state != "fuera" and directive == "#else":
            state = "else"
        elif state != "fuera" and directive == "#endif":
            state = "fuera"
        elif state in ("fuera", "else"):
            kept.append(line)
    if state != "fuera":
        raise RuntimeError(f"{relative}: bloque del motor ingenuo sin cerrar")
    return "".join(kept)


def check_standalone(archive_path: Path) -> None:
    """El ZIP tiene que funcionar solo: compila el motor y anima su salida."""
    with tempfile.TemporaryDirectory() as directory:
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(directory)
        subprocess.run(["make", "-C", f"{directory}/cpp", "release"], check=True,
                       capture_output=True, text=True)
        engine = f"{directory}/cpp/build/release/tp3"
        version = subprocess.run([engine, "--version"], check=True, capture_output=True,
                                 text=True)
        print(f"el ZIP compila solo: {version.stdout.strip()}")

        trajectory = f"{directory}/prueba.txt"
        subprocess.run([engine, "simulate", "--n", "30", "--seed", "1", "--tmax", "2",
                        "--save-every", "10", "--output", trajectory],
                       check=True, capture_output=True, text=True)
        subprocess.run([str(PYTHON), "-m", "tp3analysis.animar", trajectory,
                        "--video", f"{directory}/prueba.mp4",
                        "--fotograma", f"{directory}/prueba.png"],
                       check=True, capture_output=True, text=True,
                       cwd=directory, env={"PYTHONPATH": f"{directory}/python/src",
                                           "MPLCONFIGDIR": f"{directory}/.mpl",
                                           "PATH": "/usr/bin:/bin"})
        if not (Path(directory) / "prueba.mp4").stat().st_size:
            raise RuntimeError("la animación del ZIP no produjo video")
        print("la animación del ZIP funciona sola sobre la salida del motor")


def main() -> int:
    if not CONFIG.exists() or not PRESENTATION.exists():
        raise FileNotFoundError("faltan la configuración final o la presentación compilada")
    DELIVERY.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CONFIG, DELIVERY / CONFIG.name)
    shutil.copyfile(PRESENTATION, DELIVERED_PRESENTATION)
    (DELIVERY / PRESENTATION.name).unlink(missing_ok=True)

    sources = [ROOT / "cpp/Makefile"]
    sources += sorted((ROOT / "cpp/include/tp3").glob("*.hpp"))
    sources += sorted((ROOT / "cpp/src").glob("*.cpp"))
    with zipfile.ZipFile(CODE_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sources:
            relative = str(source.relative_to(ROOT))
            if relative in NAIVE_FILES:
                continue
            archive.writestr(relative, without_naive(relative, source.read_text(encoding="utf-8")))
        for relative in ANIMATION_FILES:
            archive.write(ROOT / relative, relative)

    if CODE_ZIP.stat().st_size >= 100_000:
        raise RuntimeError(f"el ZIP supera 100 KB: {CODE_ZIP.stat().st_size} bytes")
    with zipfile.ZipFile(CODE_ZIP) as archive:
        names = archive.namelist()
        python = {name for name in names if name.startswith("python/")}
        if python != set(ANIMATION_FILES):
            raise RuntimeError(f"el ZIP tiene código Python ajeno a la animación: {sorted(python)}")
        if any("test" in name or "build" in name for name in names):
            raise RuntimeError("el ZIP contiene archivos ajenos al motor final")
        if any("naive" in archive.read(name).decode("utf-8").lower() for name in names):
            raise RuntimeError("el ZIP todavía menciona el motor ingenuo")
    check_standalone(CODE_ZIP)
    print(f"{CODE_ZIP.name}: {CODE_ZIP.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
