from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tp2analysis.cim import (
    read_cim_summaries,
    read_tp1_cim,
    summarize_cim,
    write_cim_summaries,
)
from tp2analysis.data import Observation


class CimTests(unittest.TestCase):
    def test_summarizes_round_trips_and_reads_tp1(self) -> None:
        rows = [
            Observation("vicsek", 2.0, 0.5, 1, 0, 0.2, 1.0, 100, 3, 20, 200),
            Observation("vicsek", 2.0, 0.5, 1, 1, 0.3, 1.0, 200, 4, 22, 200),
        ]
        result = summarize_cim(rows)
        self.assertEqual(result[0].samples, 2)
        self.assertAlmostEqual(result[0].mean_time_ns, 150.0)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = root / "tp2.csv"
            write_cim_summaries(summary, result)
            self.assertEqual(read_cim_summaries(summary), result)

            tp1 = root / "tp1.csv"
            tp1.write_text(
                "regime,boundary,N,L,density,rc,M,method,samples,"
                "seed_count,mean_time_ns,stddev_time_ns,"
                "mean_neighbor_pairs,mean_distance_evaluations\n"
                "fixed,periodic,200,10,2,1,9,cim,10,10,300,20,1,2\n",
                encoding="utf-8",
            )
            loaded = read_tp1_cim(tp1)
            self.assertEqual(len(loaded), 1)
            label = next(iter(loaded))
            self.assertTrue(label.startswith("TP1"))
            self.assertEqual(loaded[label], [(200, 300.0, 20.0)])


if __name__ == "__main__":
    unittest.main()
