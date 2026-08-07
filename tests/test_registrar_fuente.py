from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/registrar_fuente.py"
SPEC = importlib.util.spec_from_file_location("registrar_fuente", SCRIPT)
assert SPEC and SPEC.loader
registrar_fuente = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registrar_fuente)


class RegistrarFuenteTests(unittest.TestCase):
    def test_registra_original_oficial_y_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            incoming = root / "material/entrada/clase.txt"
            incoming.parent.mkdir(parents=True)
            incoming.write_bytes(b"contenido oficial\n")
            result = registrar_fuente.main(
                [
                    str(incoming),
                    "--root",
                    str(root),
                    "--id",
                    "t01",
                    "--tipo",
                    "teoria",
                    "--titulo",
                    "Primera clase",
                    "--ciclo",
                    "2026",
                    "--mover",
                ]
            )
            self.assertEqual(result, 0)
            destination = root / "material/catedra/teoria/clase.txt"
            self.assertEqual(destination.read_bytes(), b"contenido oficial\n")
            self.assertFalse(incoming.exists())
            catalog = (root / "material/catalogo.tsv").read_text(encoding="utf-8")
            self.assertIn("T01\tteoria\tPrimera clase\tmaterial/catedra/teoria/clase.txt", catalog)
            expected = hashlib.sha256(b"contenido oficial\n").hexdigest()
            checksums = (root / "material/checksums.sha256").read_text(encoding="utf-8")
            self.assertEqual(checksums, f"{expected}  material/catedra/teoria/clase.txt\n")

    def test_rechaza_id_duplicado_sin_copiar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            material = root / "material"
            material.mkdir()
            (material / "catalogo.tsv").write_text(
                "id\ttipo\ttitulo\truta\tpaginas\tciclo\testado\tarchivo_original\n"
                "T01\tteoria\tAnterior\tmaterial/catedra/teoria/anterior.txt\t\t2026\tvigente\tanterior.txt\n",
                encoding="utf-8",
            )
            incoming = root / "nuevo.txt"
            incoming.write_text("nuevo", encoding="utf-8")
            with self.assertRaises(SystemExit):
                registrar_fuente.main(
                    [str(incoming), "--root", str(root), "--id", "T01", "--tipo", "teoria", "--titulo", "Nuevo"]
                )
            self.assertFalse((root / "material/catedra/teoria/nuevo.txt").exists())

    def test_rechaza_id_no_ascii(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            incoming = root / "fuente.txt"
            incoming.write_text("contenido", encoding="utf-8")
            with self.assertRaises(SystemExit):
                registrar_fuente.main(
                    [str(incoming), "--root", str(root), "--id", "TEORÍA", "--tipo", "teoria", "--titulo", "Fuente"]
                )


if __name__ == "__main__":
    unittest.main()
