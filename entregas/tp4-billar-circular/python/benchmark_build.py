"""Compila el harness con los motores reales y una misma configuracion release."""
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TP3 = ROOT.parent / "tp3-billar-metegol"


def build():
    binary = ROOT / "cpp/build/release/benchmark"
    binary.parent.mkdir(parents=True, exist_ok=True)
    sources = [ROOT / "cpp/experiments/benchmark.cpp", *[
        TP3 / f"cpp/src/{name}.cpp" for name in ["collisions", "generation", "geometry", "io", "simulation"]]]
    command = [os.environ.get("CXX", "c++"), "-std=c++20", "-O3", "-DNDEBUG", "-Wall", "-Wextra",
               "-Wpedantic", "-Werror", "-I" + str(ROOT / "cpp/include"), "-I" + str(TP3 / "cpp/include"),
               *map(str, sources), "-o", str(binary)]
    subprocess.run(command, check=True)
    return binary, sources, command


if __name__ == "__main__":
    print(build()[0])
