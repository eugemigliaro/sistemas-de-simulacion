"""Lee salidas reales del motor; se saltea si el binario no está compilado."""
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tp4analysis import conversion, energy, files, oscillator

ENGINE = Path(__file__).resolve().parents[2] / "cpp/build/release/tp4"


@unittest.skipUnless(ENGINE.exists(), "motor sin compilar: make release")
class EngineOutputTest(unittest.TestCase):
    def run_engine(self, *arguments: str) -> Path:
        folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        output = folder / "out.txt"
        subprocess.run([ENGINE, *arguments, "--output", output], check=True)
        return output

    def test_billiard_conserves_energy_and_only_converts_forward(self):
        path = self.run_engine("billiard", "--n", "100", "--dt", "1e-5", "--tf", "2", "--output-every", "1000",
                               "--x0", "0.0175", "--seed", "4")
        trajectory = files.read_billiard(path)
        self.assertEqual(trajectory.states.shape, (201, 100, 5))
        deviation = energy.relative_deviation(energy.total_energy(trajectory))
        self.assertLess(deviation.max(), 1e-4)
        used = trajectory.used.astype(int)
        self.assertTrue(np.all(np.diff(used, axis=0) >= 0))
        self.assertGreater(conversion.used_fraction(trajectory)[-1], 0.0)

    def test_oscillator_converges_to_the_exact_solution(self):
        errors = []
        for dt in ("1e-3", "5e-4"):
            header, times, positions = files.read_oscillator(
                self.run_engine("oscillator", "--integrator", "beeman", "--dt", dt))
            errors.append(oscillator.mean_squared_error(header, times, positions))
        self.assertGreater(errors[0] / errors[1], 14.0)


if __name__ == "__main__":
    unittest.main()
