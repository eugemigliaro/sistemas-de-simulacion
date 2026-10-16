from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from position_analysis import used_fraction,summarize_positions


class PositionTests(unittest.TestCase):
    def test_fu_includes_contact_at_query_time(self):
        np.testing.assert_array_equal(used_fraction([-1,2,4,4],.5,[0,1,2,3]),[0,.25,.75,.75])
        with self.assertRaises(ValueError):used_fraction([-2,1],.1,[0,1])

    def test_complete_group_sample_deviation(self):
        cases=[dict(n=20,obstacle_x=.2,duration=100,conversion=dict(t90_s=t,fu_final=1)) for t in [10,12,14,16,18]]
        row=summarize_positions(cases)[0]
        self.assertEqual(row["t90_mean_s"],14)
        self.assertAlmostEqual(row["t90_std_s"],np.sqrt(10))

    def test_censored_group_has_no_unconditional_mean(self):
        cases=[dict(n=100,obstacle_x=.1,duration=100,conversion=dict(t90_s=t,fu_final=.8)) for t in [20,None]]
        row=summarize_positions(cases)[0]
        self.assertIsNone(row["t90_mean_s"])
        self.assertEqual(row["censored"],1)
        self.assertEqual(row["t90_mean_lower_bound_s"],60)


if __name__=="__main__":unittest.main()
