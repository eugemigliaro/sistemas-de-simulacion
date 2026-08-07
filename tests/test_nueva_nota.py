from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NuevaNotaTests(unittest.TestCase):
    def test_tema_con_separadores_se_conserva(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            (root / "notas/bandeja").mkdir(parents=True)
            shutil.copy2(ROOT / "scripts/nueva_nota.sh", root / "scripts/nueva_nota.sh")
            shutil.copy2(ROOT / "notas/PLANTILLA.md", root / "notas/PLANTILLA.md")
            topic = "joins / group & order"
            result = subprocess.run(
                [str(root / "scripts/nueva_nota.sh"), topic],
                check=True,
                capture_output=True,
                text=True,
            )
            note = Path(result.stdout.strip())
            self.assertTrue(note.is_file())
            self.assertIn(topic, note.read_text(encoding="utf-8"))
            self.assertNotIn("/", note.name)


if __name__ == "__main__":
    unittest.main()
