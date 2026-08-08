"""Prueba integral del comando plot-n."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tp1viz.cli import main
from tp1viz.metrics import REQUIRED_COLUMNS


class PlotNCliTest(unittest.TestCase):
    def _write_metrics(
        self,
        path: Path,
        systems: list[tuple[int, float, int]],
    ) -> None:
        with path.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=REQUIRED_COLUMNS)
            writer.writeheader()
            for particle_count, side, cells_per_side in systems:
                times = (
                    (1, particle_count * 1_000),
                    (2, particle_count * 1_200),
                )
                for repetition, time_ns in times:
                    writer.writerow(
                        {
                            "seed": 42,
                            "boundary": "walls",
                            "method": "cim",
                            "N": particle_count,
                            "L": side,
                            "M": cells_per_side,
                            "rc": 1,
                            "repetition": repetition,
                            "time_ns": time_ns,
                            "neighbor_pairs": particle_count,
                            "distance_evaluations": particle_count * 5,
                        }
                    )

    def test_writes_summary_and_png(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            free = root / "free.csv"
            fixed = root / "fixed.csv"
            summary = root / "results" / "summary.csv"
            figure = root / "figures" / "time-vs-n.png"
            self._write_metrics(free, [(100, 20, 13), (200, 20, 13)])
            self._write_metrics(fixed, [(100, 10, 6), (200, 10 * 2**0.5, 9)])

            result = main(
                [
                    "plot-n",
                    "--free",
                    str(free),
                    "--fixed",
                    str(fixed),
                    "--summary",
                    str(summary),
                    "--figure",
                    str(figure),
                    "--log-x",
                    "--log-y",
                ]
            )

            self.assertEqual(result, 0)
            self.assertEqual(figure.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            with summary.open(encoding="utf-8") as summary_file:
                rows = list(csv.DictReader(summary_file))
            self.assertEqual(len(rows), 4)
            self.assertEqual({row["regime"] for row in rows}, {"free", "fixed"})


if __name__ == "__main__":
    unittest.main()
