"""Pruebas del post-proceso con una salida sintética del motor."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tp5analysis.io import iter_frames, read_run  # noqa: E402
from tp5analysis.observables import evacuation_time, flow, mode_counts, population  # noqa: E402

SAMPLE = """# tp5 problema 2: evacuacion con SFM sin fuerza social
# scheme hybrid agents 3 side 10 door 0.8 desired_speed 1.5
# tau 0.5 kn 120000 kt 240000 noise 0 noise_time 0.1
agent 0 0.200000 69.220000
agent 1 0.210000 76.310000
agent 2 0.180000 56.060000
mode 0.000000000 0 1
mode 0.000000000 1 1
mode 0.000000000 2 0
frame 0.000000 3
0 1.0 2.0 0.0 -1.5 1
1 3.0 4.0 0.0 -1.5 1
2 5.0 1.0 0.0 -1.5 0
mode 1.500000000 0 0
exit 2.000000000 2
frame 2.000000 2
0 1.0 0.5 0.0 -1.0 0
1 3.0 1.0 0.0 -1.5 1
exit 3.000000000 0
exit 5.000000000 1
# end_time 5.000000000 steps 2500 events 3 agent_steps 6000 switches 1
# isolated_unrelaxed_steps 10 clogged 0
# exited 3 remaining 0 bound_violations 0 max_speed 1.500000 wall_seconds 0.010000
"""


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "run.txt"
        self.path.write_text(SAMPLE)

    def tearDown(self):
        self.dir.cleanup()

    def test_read(self):
        run = read_run(self.path)
        self.assertEqual(run.agents, 3)
        self.assertEqual(run.scheme, "hybrid")
        self.assertEqual(run.frame_count, 2)
        self.assertTrue(run.finished)
        self.assertEqual(run.summary["clogged"], 0)
        self.assertAlmostEqual(run.mass[2], 56.06)

    def test_population_and_evacuation(self):
        run = read_run(self.path)
        np.testing.assert_array_equal(population(run, np.array([0.0, 2.0, 4.0, 6.0])), [3, 2, 1, 0])
        self.assertEqual(evacuation_time(run), 5.0)
        self.assertGreater(flow(run, 0.0, 1.0), 0.0)

    def test_modes(self):
        run = read_run(self.path)
        ed, ts = mode_counts(run, np.array([0.0, 1.0, 1.6, 2.5, 4.0]))
        np.testing.assert_array_equal(ed, [2, 2, 1, 1, 1])
        np.testing.assert_array_equal(ts, [1, 1, 2, 1, 0])

    def test_frames(self):
        frames = list(iter_frames(self.path))
        self.assertEqual(len(frames), 2)
        np.testing.assert_array_equal(frames[1].ids, [0, 1])
        np.testing.assert_allclose(frames[1].position[0], [1.0, 0.5])
        self.assertEqual(frames[1].mode[1], 1)


if __name__ == "__main__":
    unittest.main()
