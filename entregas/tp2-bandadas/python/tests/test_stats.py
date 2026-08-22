from __future__ import annotations

import unittest

from tp2analysis.data import Observation
from tp2analysis.stats import block_summaries, summarize


def observation(seed: int, time: float, va: float, cluster: float) -> Observation:
    return Observation(
        model="vicsek",
        density=2.0,
        eta=0.25,
        seed=seed,
        time=time,
        polarization=va,
        largest_cluster_fraction=cluster,
        cim_time_ns=100,
        neighbor_pairs=10,
        distance_evaluations=20,
    )


class StatsTests(unittest.TestCase):
    def test_temporal_then_ensemble_summary(self) -> None:
        rows = [
            observation(1, 0, 0.0, 0.1),
            observation(1, 10, 0.7, 0.5),
            observation(1, 20, 0.9, 0.7),
            observation(2, 0, 0.0, 0.1),
            observation(2, 10, 0.5, 0.3),
            observation(2, 20, 0.7, 0.5),
        ]
        result = summarize(rows, stationary_start=10)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].realizations, 2)
        self.assertAlmostEqual(result[0].polarization_mean, 0.7)
        self.assertAlmostEqual(result[0].cluster_mean, 0.5)
        self.assertAlmostEqual(result[0].polarization_std, 0.14142135623730953)

    def test_block_summaries_use_half_open_intervals(self) -> None:
        rows = [
            observation(1, 0, 0.1, 0.2),
            observation(1, 1, 0.3, 0.4),
            observation(1, 2, 0.5, 0.6),
            observation(1, 3, 0.7, 0.8),
        ]
        result = block_summaries(rows, block_size=2)
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result[0].polarization_mean, 0.2)
        self.assertAlmostEqual(result[1].polarization_mean, 0.6)

    def test_block_summaries_discard_partial_last_block(self) -> None:
        rows = [
            observation(1, 0, 0.1, 0.2),
            observation(1, 1, 0.3, 0.4),
            observation(1, 2, 0.5, 0.6),
        ]
        result = block_summaries(rows, block_size=2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].samples, 2)

    def test_block_size_must_be_an_integer_multiple_of_dt(self) -> None:
        rows = [
            observation(1, 0, 0.1, 0.2),
            observation(1, 1, 0.3, 0.4),
        ]
        with self.assertRaises(ValueError):
            block_summaries(rows, block_size=1.5)

    def test_per_parameter_stationary_start(self) -> None:
        rows = [
            observation(1, 0, 0.1, 0.2),
            observation(1, 10, 0.5, 0.6),
            observation(1, 20, 0.7, 0.8),
        ]
        starts = {("vicsek", 2.0, 0.25): 10.0}
        result = summarize(rows, starts)
        self.assertAlmostEqual(result[0].polarization_mean, 0.6)

    def test_rejects_duplicate_times_and_truncated_realizations(self) -> None:
        duplicate = [
            observation(1, 0, 0.1, 0.2),
            observation(1, 0, 0.3, 0.4),
        ]
        with self.assertRaises(ValueError):
            summarize(duplicate, 0)

        truncated = [
            observation(1, 0, 0.1, 0.2),
            observation(1, 1, 0.2, 0.3),
            observation(1, 2, 0.3, 0.4),
            observation(2, 0, 0.1, 0.2),
            observation(2, 1, 0.2, 0.3),
        ]
        with self.assertRaises(ValueError):
            summarize(truncated, 0)


if __name__ == "__main__":
    unittest.main()
