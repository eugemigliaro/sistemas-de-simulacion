"""Prueba integral del comando plot-neighbors."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tp1viz.cli import main


class PlotNeighborsCliTest(unittest.TestCase):
    def test_writes_png(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            static = root / "static.txt"
            dynamic = root / "dynamic.txt"
            neighbors = root / "neighbors.txt"
            figure = root / "figures" / "neighbors.png"
            static.write_text("3\n10\n0.5 1\n0.5 1\n0.5 1\n", encoding="utf-8")
            dynamic.write_text(
                "0\n2 2 0 0\n3 2 0 0\n8 8 0 0\n", encoding="utf-8"
            )
            neighbors.write_text("1,2\n2,1\n3\n", encoding="utf-8")

            result = main(
                [
                    "plot-neighbors",
                    "--static",
                    str(static),
                    "--dynamic",
                    str(dynamic),
                    "--neighbors",
                    str(neighbors),
                    "--particle",
                    "1",
                    "--rc",
                    "1",
                    "--figure",
                    str(figure),
                ]
            )

            self.assertEqual(result, 0)
            self.assertEqual(figure.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
