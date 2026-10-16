from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from speed_analysis import histogram, mb_bins, fit_theta, stationary_suffix


class SpeedTests(unittest.TestCase):
    def test_histogram_normalization_and_tail(self):
        edges=np.array([0,.5,1,2])
        self.assertAlmostEqual(float(np.sum(histogram([0,.5,1,2],edges)*np.diff(edges))),1)
        with self.assertRaises(ValueError): histogram([2.1],edges)
        with self.assertRaises(ValueError): histogram([-1],edges)

    def test_recovers_theoretical_parameter_without_amplitude(self):
        edges=np.linspace(0,5,51)
        theta=.0113
        result,error=fit_theta(mb_bins(edges,.025,theta),edges,.025,.0125)
        self.assertAlmostEqual(result,theta,places=10)
        self.assertLess(error,1e-16)
        self.assertAlmostEqual(float(np.sum(mb_bins(edges,.025,theta)*np.diff(edges))),1,places=10)

    def test_known_cdf_not_gaussian_in_velocity_component(self):
        np.testing.assert_allclose(mb_bins(np.array([0,1,2]),2,1),
                                   [1-np.exp(-1),np.exp(-1)-np.exp(-4)])

    def test_suffix_requires_consecutive_comparisons_and_shape(self):
        rows=[[1,0],[.5,.5],[.5,.5],[.5,.5],[.5,.5]]
        start,tv,_=stationary_suffix(rows,[1]*5,[0,1,2],.05,.02)
        self.assertEqual(start,1)
        self.assertAlmostEqual(tv[0],.5)
        self.assertIsNone(stationary_suffix(rows[:4],[1]*4,[0,1,2],.05,.02)[0])


if __name__=="__main__": unittest.main()
