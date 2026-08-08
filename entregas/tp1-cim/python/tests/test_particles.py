"""Pruebas de lectura de los archivos de partículas y vecinos."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tp1viz.particles import ParticleDataError, read_neighbors, read_system


class ParticleFilesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.static = self.root / "static.txt"
        self.dynamic = self.root / "dynamic.txt"
        self.neighbors = self.root / "neighbors.txt"
        self.static.write_text("3\n20\n0.25 1\n0.24 1\n0.26 1\n", encoding="utf-8")
        self.dynamic.write_text(
            "0\n1 2 0 0\n3 4 0 0\n5 6 0 0\n", encoding="utf-8"
        )
        self.neighbors.write_text("1,2\n2,1\n3\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_reads_system_and_symmetric_neighbors(self) -> None:
        system = read_system(self.static, self.dynamic)
        neighbors = read_neighbors(self.neighbors, len(system.particles))

        self.assertEqual(system.side, 20)
        self.assertEqual(system.particles[1].id, 2)
        self.assertEqual(system.particles[1].x, 3)
        self.assertEqual(neighbors, (frozenset({2}), frozenset({1}), frozenset()))

    def test_rejects_asymmetric_neighbors(self) -> None:
        self.neighbors.write_text("1,2\n2\n3\n", encoding="utf-8")

        with self.assertRaises(ParticleDataError):
            read_neighbors(self.neighbors, 3)


if __name__ == "__main__":
    unittest.main()
