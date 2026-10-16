from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from performance_analysis import conversion_times, summarize, summarize_density


class PerformanceTests(unittest.TestCase):
    def test_thresholds_and_censoring(self):
        state = np.zeros((10, 9))
        state[:, 8] = [1, 2, 3, 4, 5, 6, 7, 8, 9, -1]
        self.assertEqual(conversion_times(state, .1, 3), dict(t90_s=.9, t100_s=None, fu_final=.9))
        state[8, 8] = -1
        self.assertIsNone(conversion_times(state, .1, 3)["t90_s"])

    def test_sample_standard_deviation(self):
        cases = [dict(engine="tp4", n=10, runtime_seconds=t) for t in [1, 3]]
        result = summarize(cases)[0]
        self.assertEqual(result["runtime_mean_s"], 2)
        self.assertAlmostEqual(result["runtime_std_s"], np.sqrt(2))

    def test_no_unconditional_mean_when_threshold_missing(self):
        cases = [dict(engine="tp4", n=10, final_time=30, conversion=dict(t90_s=t, t100_s=None, fu_final=.8))
                 for t in [10, None]]
        row = summarize_density(cases)[0]
        self.assertIsNone(row["t90_mean_s"])
        self.assertEqual(row["t90_censored"], 1)
        self.assertEqual(row["t90_observed_mean_s"], 10)
        self.assertEqual(row["t90_mean_lower_bound_s"], 20)


if __name__ == "__main__": unittest.main()
