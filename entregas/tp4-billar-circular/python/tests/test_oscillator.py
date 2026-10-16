from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))
from analysis import exact_position, load_trajectory, position_errors

CONFIG = dict(mass=70, stiffness=10000, damping=100, x0=1, v0=-5 / 7, duration=5)
BINARY = ROOT / "cpp/build/release/tp4"


class AnalysisTests(unittest.TestCase):
    def test_reference_initial_conditions_and_regimes(self):
        for damping, stiffness in [(0, 0), (0, 10000), (100, 10000), (140, 70), (7000, 10000)]:
            c = dict(CONFIG, damping=damping, stiffness=stiffness)
            self.assertAlmostEqual(float(exact_position(0, c)), c["x0"])
            eps = 1e-6
            derivative = (exact_position(eps, c) - exact_position(-eps, c)) / (2 * eps)
            self.assertAlmostEqual(float(derivative), c["v0"], places=6)
            self.assertTrue(np.isfinite(exact_position(np.linspace(0, 5, 100), c)).all())
        free = dict(CONFIG, damping=0, stiffness=0)
        np.testing.assert_allclose(exact_position(np.array([0, 1, 5]), free), [1, 2 / 7, -18 / 7])

    def test_ecm_excludes_initial_sample_and_uses_all_steps(self):
        c = dict(CONFIG, stiffness=0, damping=0, x0=0, v0=0, duration=2)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "known.csv"
            with path.open("w") as handle:
                handle.write("step,time,position,velocity\n0,0,0,0\n1,1,1,0\n2,2,3,0\n")
            data = load_trajectory(path, c, 2)
            self.assertEqual(position_errors(data, c), (5, 3))
            path.write_text(path.read_text().replace("2,2,3", "2,1.5,3"))
            with self.assertRaises(ValueError):
                load_trajectory(path, c, 2)

    def test_cli_rejects_invalid_input_before_writing(self):
        for args in [["--method", "wrong"], ["--steps", "0"], ["--steps", "-1"],
                     ["--steps", "2.5"], ["--duration", "nan"], ["--mass", "0"],
                     ["--damping", "-1"], ["--x0", "inf"], ["--duration", "1junk"],
                     ["--unknown", "1"], ["--steps"], ["--duration", "1", "--duration", "2"]]:
            with self.subTest(args=args), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "invalid.csv"
                command = [str(BINARY), "oscillator", "--output", str(output)]
                if "--method" not in args:
                    command += ["--method", "beeman"]
                result = subprocess.run(command + args, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)
                self.assertFalse(output.exists())

    def test_all_methods_csv_contract_and_convergence(self):
        for method in ["beeman", "verlet", "velocity-verlet", "euler-pc"]:
            with self.subTest(method=method), tempfile.TemporaryDirectory() as tmp:
                errors = []
                for steps in [1000, 2000]:
                    path = Path(tmp) / "run.csv"
                    subprocess.run([str(BINARY), "oscillator", "--method", method,
                                    "--steps", str(steps), "--output", str(path)], check=True)
                    data = load_trajectory(path, CONFIG, steps)
                    ecm, maximum = position_errors(data, CONFIG)
                    self.assertGreater(ecm, 0)
                    self.assertGreaterEqual(maximum**2, ecm)
                    errors.append(ecm)
                self.assertLess(errors[1], errors[0] / 2)

    def test_nonfinite_simulation_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([str(BINARY), "oscillator", "--method", "euler-pc",
                                     "--stiffness", "1e308", "--steps", "10", "--output",
                                     str(Path(tmp) / "run.csv")], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no finito", result.stderr)


if __name__ == "__main__":
    unittest.main()
