from __future__ import annotations

import importlib.util
import stat
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/configurar_materia.py"
SPEC = importlib.util.spec_from_file_location("configurar_materia", SCRIPT)
assert SPEC and SPEC.loader
configurar_materia = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(configurar_materia)


class ConfigurarMateriaTests(unittest.TestCase):
    def test_slugify_normaliza_acentos_y_signos(self) -> None:
        self.assertEqual(configurar_materia.slugify("Álgebra Lineal II"), "algebra-lineal-ii")
        self.assertEqual(configurar_materia.slugify("  ¿Qué sé?  "), "que-se")

    def test_configura_y_actualiza_titulo(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text(
                "<!-- course-title:start -->\n# Course Wiki Template\n<!-- course-title:end -->\n",
                encoding="utf-8",
            )
            (root / "README.md").chmod(0o644)
            result = configurar_materia.main(
                [
                    "--root",
                    str(root),
                    "--nombre",
                    "Álgebra Lineal",
                    "--institucion",
                    "Universidad Ejemplo",
                    "--herramienta",
                    "Python",
                    "--dialecto",
                    "3.12",
                ]
            )
            self.assertEqual(result, 0)
            config = (root / "materia.yaml").read_text(encoding="utf-8")
            self.assertIn('nombre: "Álgebra Lineal"', config)
            self.assertIn('slug: "algebra-lineal"', config)
            self.assertIn('herramienta: "Python"', config)
            self.assertIn("# Álgebra Lineal", (root / "README.md").read_text(encoding="utf-8"))
            self.assertEqual(stat.S_IMODE((root / "README.md").stat().st_mode), 0o644)
            self.assertTrue((root / "wiki/temas").is_dir())
            self.assertEqual(configurar_materia.validate_repo(root), [])

    def test_titulo_con_barra_invertida_no_rompe_el_readme(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            readme = root / "README.md"
            readme.write_text(
                "<!-- course-title:start -->\n# Inicial\n<!-- course-title:end -->\n",
                encoding="utf-8",
            )
            self.assertTrue(configurar_materia.update_readme_title(readme, r"Cálculo \\ Aplicado"))
            self.assertIn(r"# Cálculo \\ Aplicado", readme.read_text(encoding="utf-8"))

    def test_adopcion_minima_no_toca_contenido_existente(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            readme = root / "README.md"
            readme.write_text("# Repo existente\n", encoding="utf-8")
            existing = root / "apuntes.md"
            existing.write_text("contenido propio\n", encoding="utf-8")
            result = configurar_materia.main(
                ["--root", str(root), "--nombre", "Materia Existente", "--adoptar"]
            )
            self.assertEqual(result, 0)
            self.assertEqual(readme.read_text(encoding="utf-8"), "# Repo existente\n")
            self.assertEqual(existing.read_text(encoding="utf-8"), "contenido propio\n")
            self.assertFalse((root / "wiki").exists())
            self.assertTrue((root / "materia.yaml").is_file())


if __name__ == "__main__":
    unittest.main()
