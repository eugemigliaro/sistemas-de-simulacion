from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from density_analysis import summarize_groups,best_positions,restricted_summary


def case(seed,t90,t100,duration=100,x=.1):
    return dict(n=20,seed=seed,obstacle_x=x,duration=duration,
                conversion=dict(t90_s=t90,t100_s=t100,fu_final=1 if t100 else .9))


class DensityTests(unittest.TestCase):
    def test_censored_times_do_not_become_complete_means(self):
        r=summarize_groups([case(1,20,40),case(2,30,None)])[0]
        self.assertEqual(r['t90_mean_s'],25)
        self.assertIsNone(r['t100_mean_s'])
        self.assertEqual(r['t100_mean_lower_bound_s'],70)

    def test_restricted_mean_has_a_distinct_interpretation(self):
        r=restricted_summary([case(1,20,40),case(2,30,None)],50)[0]
        self.assertEqual(r['t100_restricted_mean_s'],45)
        with self.assertRaises(ValueError):restricted_summary([case(1,None,None,20)],50)

    def test_censored_competitor_prevents_certifying_minimum(self):
        rows=summarize_groups([case(1,20,40),case(1,None,None,10,.2)])
        self.assertFalse(best_positions(rows)[0]['certified_on_grid'])
        rows=summarize_groups([case(1,20,40),case(1,None,None,100,.2)])
        self.assertTrue(best_positions(rows)[0]['certified_on_grid'])

    def test_duplicate_realization_rejected(self):
        with self.assertRaises(ValueError):summarize_groups([case(1,20,40),case(1,30,50)])


if __name__=='__main__':unittest.main()
