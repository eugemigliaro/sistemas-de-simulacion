import tempfile
import unittest
from pathlib import Path

import numpy as np

from tp4analysis import conversion, energy, files, oscillator, speed, stats

HEADER = """# tp4 billiard
# particles 2
# seed 1
# layout random
# radius 0.51
# particle_radius 0.0175
# particle_mass 0.025
# stiffness 10000
# initial_speed 1
# obstacle_x {obstacle}
# dt 0.001
# steps 2
# output_every 1
"""


def write_billiard(folder: Path, frames: list[list[str]], obstacle: str = "none") -> Path:
    path = folder / "run.txt"
    with open(path, "w") as stream:
        stream.write(HEADER.format(obstacle=obstacle))
        for step, lines in enumerate(frames):
            stream.write(f"frame {step} {step * 0.001}\n" + "\n".join(lines) + "\n")
    return path


class FilesTest(unittest.TestCase):
    def test_reads_header_and_frames(self):
        with tempfile.TemporaryDirectory() as folder:
            frame = ["0.1 0 1 0 0", "-0.1 0 -1 0 1"]
            path = write_billiard(Path(folder), [frame, frame, frame], obstacle="0.0175")
            trajectory = files.read_billiard(path)
        self.assertEqual(trajectory.header["particles"], 2)
        self.assertEqual(trajectory.header["obstacle_x"], 0.0175)
        self.assertEqual(trajectory.states.shape, (3, 2, 5))
        np.testing.assert_allclose(trajectory.times, [0, 0.001, 0.002])
        self.assertEqual(trajectory.used[0].tolist(), [False, True])

    def test_rejects_truncated_runs(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_billiard(Path(folder), [["0 0 0 0 0", "0.1 0 0 0 0"]] * 2)
            with self.assertRaises(ValueError):
                files.read_billiard(path)


class OscillatorTest(unittest.TestCase):
    def test_exact_solution_satisfies_the_equation(self):
        m, k, gamma = 70.0, 1e4, 100.0
        t = np.linspace(0, 1, 200001)
        x = oscillator.exact_position(t, m, k, gamma, 1.0)
        v = np.gradient(x, t)
        a = np.gradient(v, t)
        residual = m * a[5:-5] + gamma * v[5:-5] + k * x[5:-5]
        self.assertLess(np.max(np.abs(residual)), 1e-2 * k)
        self.assertAlmostEqual(x[0], 1.0)
        self.assertAlmostEqual(v[0], -gamma / (2 * m), places=3)

    def test_exact_samples_have_zero_error(self):
        header = {"mass": 70.0, "stiffness": 1e4, "damping": 100.0, "amplitude": 1.0}
        t = np.linspace(0, 5, 501)
        x = oscillator.exact_position(t, 70.0, 1e4, 100.0, 1.0)
        self.assertEqual(oscillator.mean_squared_error(header, t, x), 0.0)
        self.assertAlmostEqual(oscillator.mean_squared_error(header, t, x + 1e-3), 1e-6)


class EnergyTest(unittest.TestCase):
    def test_counts_each_spring_once(self):
        overlap = 0.001
        d = 2 * 0.0175 - overlap
        with tempfile.TemporaryDirectory() as folder:
            frame = [f"{-d / 2} 0 1 0 0", f"{d / 2} 0 -1 0 0"]
            trajectory = files.read_billiard(write_billiard(Path(folder), [frame] * 3))
        expected = 2 * 0.5 * 0.025 * 1.0 + 0.5 * 1e4 * overlap**2
        np.testing.assert_allclose(energy.total_energy(trajectory), expected, rtol=1e-9)

    def test_includes_wall_and_obstacles(self):
        with tempfile.TemporaryDirectory() as folder:
            frame = ["0.4935 0 0 0 0", "0.0515 0 0 0 1"]
            trajectory = files.read_billiard(write_billiard(Path(folder), [frame] * 3, obstacle="0.0175"))
        wall, obstacle = 0.4935 + 0.0175 - 0.51, 0.035 - (0.0515 - 0.0175)
        expected = 0.5 * 1e4 * (wall**2 + obstacle**2)
        np.testing.assert_allclose(energy.total_energy(trajectory), expected, rtol=1e-6)


class ConversionTest(unittest.TestCase):
    def test_crossing_times(self):
        times = np.array([0.0, 1.0, 2.0, 3.0])
        fraction = np.array([0.0, 0.5, 0.9, 0.95])
        self.assertEqual(conversion.crossing_time(times, fraction, 0.9), 2.0)
        self.assertIsNone(conversion.crossing_time(times, fraction, 1.0))

    def test_fraction_from_colors(self):
        with tempfile.TemporaryDirectory() as folder:
            frames = [["0 0 0 0 0", "0.1 0 0 0 0"], ["0 0 0 0 1", "0.1 0 0 0 0"], ["0 0 0 0 1", "0.1 0 0 0 1"]]
            summary = conversion.summarize_run(files.read_billiard(write_billiard(Path(folder), frames)))
        np.testing.assert_allclose(summary["fu"], [0, 0.5, 1])
        self.assertEqual(summary["t90"], 0.002)
        self.assertEqual(summary["t100"], 0.002)


class SpeedTest(unittest.TestCase):
    def test_model_is_a_density(self):
        v = np.linspace(0, 5, 50001)
        density = speed.maxwell_boltzmann(v, 0.025, 0.0125)
        self.assertAlmostEqual(np.trapezoid(density, v), 1.0, places=6)
        self.assertAlmostEqual(np.trapezoid(0.5 * 0.025 * v**2 * density, v), 0.0125, places=6)

    def test_fit_recovers_the_thermal_energy(self):
        rng = np.random.default_rng(3)
        mass, thermal = 0.025, 0.0125
        samples = np.linalg.norm(rng.normal(0, np.sqrt(thermal / mass), size=(400000, 2)), axis=1)
        edges = np.arange(0, 4.05, 0.1)
        density = speed.probability_density(samples, edges)
        centers = 0.5 * (edges[1:] + edges[:-1])
        best, grid, errors = speed.fit_thermal_energy(centers, density, mass, 0.001, 0.05)
        self.assertAlmostEqual(best / thermal, 1.0, delta=0.01)
        self.assertEqual(len(grid), len(errors))


class StatsTest(unittest.TestCase):
    def test_censored_mean(self):
        self.assertEqual(stats.censored_mean([1.0, None, 3.0])["missing"], 1)
        self.assertIsNone(stats.censored_mean([1.0, None])["mean"])
        complete = stats.censored_mean([1.0, 3.0])
        self.assertEqual(complete["mean"], 2.0)
        self.assertAlmostEqual(complete["std"], np.sqrt(2))

    def test_significant_figures(self):
        self.assertEqual(stats.significant(45.4321, 0.31), ("45.4", "0.3"))
        self.assertEqual(stats.significant(13.62, 1.04), ("13.6", "1.0"))
        self.assertEqual(stats.significant(0.0124031, 0.00007), ("0.01240", "0.00007"))
        self.assertEqual(stats.significant(14.675, 1.56), ("14.7", "1.6"))


if __name__ == "__main__":
    unittest.main()
