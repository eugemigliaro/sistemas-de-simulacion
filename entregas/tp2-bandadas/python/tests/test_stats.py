from __future__ import annotations

import unittest

from tp2analysis.data import Observation
from tp2analysis.stats import summarize


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


if __name__ == "__main__":
    unittest.main()
