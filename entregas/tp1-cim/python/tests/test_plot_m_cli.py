"""Prueba integral del comando plot-m."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tp1viz.cli import main
from tp1viz.metrics import REQUIRED_COLUMNS


class PlotMCliTest(unittest.TestCase):
    def test_writes_summary_and_png(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "metrics.csv"
            summary = root / "results" / "summary.csv"
            figure = root / "figures" / "time-vs-m.png"
            with source.open("w", newline="", encoding="utf-8") as output:
                writer = csv.DictWriter(output, fieldnames=REQUIRED_COLUMNS)
                writer.writeheader()
                for cells_per_side, method in ((1, "brute_force"), (2, "cim")):
                    for repetition, time_ns in ((1, 1_000), (2, 3_000)):
                        writer.writerow(
                            {
                                "seed": 42,
                                "boundary": "walls",
                                "method": method,
                                "N": 100,
                                "L": 20,
                                "M": cells_per_side,
                                "rc": 1,
                                "repetition": repetition,
                                "time_ns": time_ns,
                                "neighbor_pairs": 7,
                                "distance_evaluations": 20,
                            }
                        )

            result = main(
                [
                    "plot-m",
                    str(source),
                    "--summary",
                    str(summary),
                    "--figure",
                    str(figure),
                ]
            )

            self.assertEqual(result, 0)
            self.assertTrue(summary.is_file())
            self.assertEqual(figure.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
