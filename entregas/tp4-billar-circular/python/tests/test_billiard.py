import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))
from billiard_analysis import Energy, frames, energy_series, maximum_relative_error

BINARY = ROOT / "cpp/build/release/tp4"
CONFIG = dict(n=2, mass=.025, stiffness=10000, radius=.51, particle_radius=.0175,
              obstacles=False, obstacle_x=.1)


class BilliardTests(unittest.TestCase):
    def test_independent_energy_components(self):
        state = np.zeros((2, 9))
        state[:, 8] = -1
        state[:, 3] = [-.015, .015]
        state[:, 5] = [1, -1]
        kinetic, pair, wall, obstacle = Energy(CONFIG).components(state)
        self.assertAlmostEqual(kinetic, .025)
        self.assertAlmostEqual(pair, .125)
        self.assertEqual(wall, 0)
        self.assertEqual(obstacle, 0)
        one = state[:1].copy()
        one[0, 3:5] = [.5, 0]
        c = dict(CONFIG, n=1)
        self.assertAlmostEqual(Energy(c).components(one)[2], .28125)
        one[0, 3:5] = [.13, 0]
        self.assertAlmostEqual(Energy(dict(c, obstacles=True)).components(one)[3], .125)

    def test_initialization_and_complete_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.csv"
            subprocess.run([str(BINARY), "billiard", "--n", "30", "--duration", ".02", "--dt", ".0001",
                            "--save-every", "10", "--seed", "42", "--obstacles", "1", "--output", str(path)], check=True)
            c = json.loads(Path(str(path) + ".json").read_text())
            snapshots = list(frames(path, c))
            self.assertEqual(len(snapshots), 21)
            p = snapshots[0][2][:, 3:5]
            delta = p[:, None] - p[None, :]
            distances = np.sqrt(np.sum(delta**2, axis=2))
            distances += np.eye(30)
            self.assertGreaterEqual(np.min(distances), .035)
            self.assertTrue(np.all(np.linalg.norm(p, axis=1) <= .4925))
            np.testing.assert_allclose(np.linalg.norm(snapshots[0][2][:, 5:7], axis=1), 1, atol=1e-14)
            for x in [-.0175, .0175]:
                self.assertTrue(np.all(np.linalg.norm(p - [x, 0], axis=1) >= .035))
            self.assertAlmostEqual(sum(Energy(c).components(snapshots[0][2])), 30 * .025 / 2)

    def test_conversion_time_survives_sparse_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            initial = Path(tmp) / "initial.csv"
            initial.write_text("id,x,y,vx,vy\n0,0.2,0,-1,0\n")
            observed = []
            for stride in [1, 1000]:
                path = Path(tmp) / f"run-{stride}.csv"
                subprocess.run([str(BINARY), "billiard", "--n", "1", "--duration", ".08", "--dt", ".000002",
                                "--save-every", str(stride), "--initial", str(initial), "--obstacles", "1",
                                "--obstacle-x", ".1", "--output", str(path)], check=True)
                c = json.loads(Path(str(path) + ".json").read_text())
                last = None
                for _, _, state in frames(path, c):
                    last = state
                self.assertEqual(last[0, 7], 1)
                observed.append(last[0, 8])
            self.assertEqual(*observed)
            self.assertLessEqual(abs(observed[0] * .000002 - .065), .000004)

    def test_invalid_cli_and_initial_state(self):
        cases = [["--n", "0"], ["--dt", "0"], ["--dt", ".003"], ["--save-every", "0"],
                 ["--steps", "11", "--save-every", "2"], ["--n", "-2"], ["--radius", "nan"],
                 ["--mass", "0"], ["--obstacles", "yes"], ["--obstacles", "1", "--obstacle-x", "0"],
                 ["--steps", "10", "--dt", ".1"], ["--unknown", "1"]]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.csv"
            for case in cases:
                with self.subTest(case=case):
                    result = subprocess.run([str(BINARY), "billiard", "--output", str(path), *case], capture_output=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(path.exists())
            initial = Path(tmp) / "overlap.csv"
            initial.write_text("id,x,y,vx,vy\n0,0,0,1,0\n1,0,0,-1,0\n")
            result = subprocess.run([str(BINARY), "billiard", "--n", "2", "--initial", str(initial),
                                     "--output", str(path)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(path.exists())

    def test_incomplete_and_reversed_state_rejected(self):
        c = dict(CONFIG, n=1, steps=2, save_every=1, dt=.1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.csv"
            prefix = "step,time,id,x,y,vx,vy,used,first_contact_step\n0,0,0,0,0,1,0,0,-1\n"
            path.write_text(prefix + "1,.1,0,0,0,1,0,1,1\n2,.2,0,0,0,1,0,0,-1\n")
            with self.assertRaises(ValueError):
                list(frames(path, c))
            path.write_text(prefix)
            with self.assertRaises(ValueError):
                list(frames(path, c))

    def test_sampling_can_hide_energy_peak(self):
        series = np.array([[0, 0, 1], [1, .1, 1.01], [2, .2, 1]])
        self.assertAlmostEqual(maximum_relative_error(series), .01)
        self.assertEqual(maximum_relative_error(series[::2]), 0)


if __name__ == "__main__":
    unittest.main()
