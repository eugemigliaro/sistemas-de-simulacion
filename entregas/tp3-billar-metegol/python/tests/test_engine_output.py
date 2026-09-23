"""Post-proceso sobre salida real del motor.

Se saltea si el binario no está compilado (make debug o make release).
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tp3analysis.cli import main
from tp3analysis.goals import goal_curve, time_to_fraction
from tp3analysis.msd import trajectory_msd
from tp3analysis.trajectory import read_trajectory


ROOT = Path(__file__).resolve().parents[2]
# `make test` garantiza que el binario debug esta actualizado antes de correr
# estas pruebas. El release puede existir de una compilacion anterior, asi que
# usarlo primero haria que la integracion probara codigo obsoleto.
BINARIES = [ROOT / "cpp/build/debug/tp3", ROOT / "cpp/build/release/tp3"]
ENGINE = next((path for path in BINARIES if path.exists()), None)


@unittest.skipIf(ENGINE is None, "motor sin compilar")
class EngineOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.directory = tempfile.TemporaryDirectory()
        cls.paths = []
        for seed in (1, 2):
            path = Path(cls.directory.name) / f"run{seed}.txt"
            subprocess.run(
                [str(ENGINE), "simulate", "--n", "100", "--seed", str(seed),
                 "--tmax", "30", "--save-every", "40", "--output", str(path)],
                check=True, capture_output=True,
            )
            cls.paths.append(path)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.directory.cleanup()

    def test_goal_curve_is_consistent_with_the_engine(self) -> None:
        trajectory = read_trajectory(self.paths[0])
        self.assertTrue(trajectory.complete)
        self.assertTrue(trajectory.reached_max_time)
        curve = goal_curve(trajectory)
        self.assertTrue(np.all(np.diff(curve.goals) == 1))
        result = time_to_fraction(trajectory)
        self.assertEqual(result.ended_by, "max_time")
        if result.reached:
            self.assertLessEqual(result.t90, 30.0)

    def test_msd_saturates_at_the_confined_value(self) -> None:
        # Para posiciones uniformes e independientes en la caja accesible
        # (L − 2r) × (W − 2r), <|Δr|²> → [(L − 2r)² + (W − 2r)²]/6. Si el DCM
        # se estanca ahí las partículas están bien confinadas.
        trajectory = read_trajectory(self.paths[0])
        header = trajectory.header
        side_x = header.length - 2 * header.particle_radius
        side_y = header.width - 2 * header.particle_radius
        saturation = (side_x**2 + side_y**2) / 6
        curve = trajectory_msd(trajectory, 0.1, 10.0)
        late = curve.msd[curve.lags > 8.0]
        self.assertLess(abs(late.mean() / saturation - 1), 0.15)
        # Y a desfasajes cortos es balístico: <|Δr|²> ≈ v0²τ².
        early = curve.lags < 0.02
        if np.any(early):
            ratio = curve.msd[early] / curve.lags[early] ** 2
            self.assertLess(abs(ratio.mean() - 1), 0.3)

    def test_cli_end_to_end(self) -> None:
        output = Path(self.directory.name) / "out"
        paths = [str(path) for path in self.paths]
        self.assertEqual(main(["t90", *paths, "--output", str(output / "t90.csv")]), 0)
        self.assertEqual(main(["goals", paths[0], "--output", str(output / "goals.csv")]), 0)
        self.assertEqual(main([
            "diffusion", *paths, "--window", "0.3", "1.5", "--max-lag", "3",
            "--output-dir", str(output / "diffusion"),
        ]), 0)
        for name in ("t90.csv", "goals.csv", "diffusion/diffusion.csv",
                     "diffusion/msd_pooled.csv", "diffusion/ec_pooled.csv",
                     "diffusion/msd_seed1.csv", "diffusion/ec_seed2.csv"):
            self.assertTrue((output / name).exists(), name)

    def test_cli_rejects_repeated_seeds(self) -> None:
        path = str(self.paths[0])
        self.assertEqual(main(["t90", path, path]), 1)


if __name__ == "__main__":
    unittest.main()
