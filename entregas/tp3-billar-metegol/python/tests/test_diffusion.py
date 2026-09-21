from __future__ import annotations

import math
import unittest

import numpy as np

from support import trajectory_text
from tp3analysis.diffusion import fit_diffusion, pool_curves, summarize_diffusion
from tp3analysis.msd import MsdCurve, msd_multiple_origins, trajectory_msd
from tp3analysis.trajectory import parse_trajectory


def ballistic(times: np.ndarray, speeds: list[float]) -> np.ndarray:
    """Partículas en línea recta sobre x: |Δr|² = v²τ² exacto."""
    return np.array([[[v * t, 0.0] for v in speeds] for t in times])


def diffusive_curve(coefficient: float, bins: np.ndarray, width: float = 0.1) -> MsdCurve:
    lags = (bins + 0.5) * width
    return MsdCurve(
        lags=lags, msd=4 * coefficient * lags, pairs=np.ones_like(bins),
        bins=bins, bin_width=width, max_lag=2.0,
    )


class MsdTests(unittest.TestCase):
    def test_ballistic_motion_with_irregular_times(self) -> None:
        # Tiempos elegidos para que ningún desfasaje caiga en un borde de
        # intervalo, donde el redondeo decidiría de qué lado queda.
        times = np.array([0.0, 0.131, 0.272, 0.343, 0.714, 0.996])
        curve = msd_multiple_origins(times, ballistic(times, [1.0, 3.0]), 0.05, 1.0)
        # Cada intervalo promedia v²τ² de sus pares: con τ² no lineal el
        # valor exacto sale de recorrer los pares a mano.
        pairs = [
            (t2 - t1) for i, t1 in enumerate(times) for t2 in times[i + 1:]
        ]
        expected: dict[int, list[float]] = {}
        for lag in pairs:
            expected.setdefault(math.ceil(lag / 0.05) - 1, []).append(lag)
        self.assertEqual(curve.bins.tolist(), sorted(expected))
        for bin_index, lag, msd, count in zip(curve.bins, curve.lags, curve.msd, curve.pairs):
            lags = np.array(expected[bin_index])
            self.assertEqual(count, lags.size)
            self.assertAlmostEqual(lag, lags.mean())
            self.assertAlmostEqual(msd, np.mean(5.0 * lags**2))

    def test_counts_every_origin(self) -> None:
        # Paso 1/8, exacto en binario: los desfasajes caen en el borde
        # superior de cada intervalo, que es cerrado.
        times = np.arange(11) * 0.125
        curve = msd_multiple_origins(times, ballistic(times, [1.0]), 0.125, 0.4)
        # Desfasajes 0.125, 0.25 y 0.375 con 10, 9 y 8 orígenes.
        self.assertEqual(curve.pairs.tolist(), [10, 9, 8])

    def test_trajectory_msd_skips_final_frame_and_duplicates(self) -> None:
        rows = lambda x: [(x, 0.3, 1.0, 0.0, 0)]
        frames = [
            (0.0, 0, "initial", rows(0.1)),
            (0.2, 1, "periodic", rows(0.3)),
            (0.2, 2, "periodic", rows(0.3)),
            (0.4, 3, "periodic", rows(0.5)),
            # Avance rectilíneo hasta tmax, no es un evento: no debe contar.
            (0.9, 3, "final", rows(1.0)),
        ]
        trajectory = parse_trajectory(trajectory_text(frames, 1))
        curve = trajectory_msd(trajectory, 0.1, 1.0)
        self.assertEqual(curve.pairs.sum(), 3)
        self.assertAlmostEqual(curve.lags.max(), 0.4)


class DiffusionTests(unittest.TestCase):
    def test_d_is_a_quarter_of_the_slope(self) -> None:
        fit = fit_diffusion(diffusive_curve(0.02, np.arange(20)), (0.3, 1.5))
        self.assertAlmostEqual(fit.coefficient, 0.02, places=10)
        self.assertEqual(fit.window, (0.3, 1.5))

    def test_window_excludes_points_outside(self) -> None:
        curve = diffusive_curve(0.02, np.arange(20))
        broken = MsdCurve(
            lags=curve.lags, msd=np.where(curve.lags > 1.0, 0.0, curve.msd),
            pairs=curve.pairs, bins=curve.bins, bin_width=0.1, max_lag=2.0,
        )
        self.assertAlmostEqual(fit_diffusion(broken, (0.2, 0.9)).coefficient, 0.02)

    def test_pooling_uses_common_bins(self) -> None:
        pooled = pool_curves([
            diffusive_curve(0.01, np.arange(0, 10)),
            diffusive_curve(0.03, np.arange(2, 12)),
        ])
        self.assertEqual(pooled.lags.size, 8)
        np.testing.assert_allclose(pooled.msd, 4 * 0.02 * pooled.lags)
        self.assertEqual(pooled.realizations, 2)

    def test_summary_gives_the_three_estimates(self) -> None:
        rng = np.random.default_rng(11)
        curves = []
        for coefficient in (0.018, 0.020, 0.022):
            curve = diffusive_curve(coefficient, np.arange(20))
            noisy = curve.msd + rng.normal(0, 1e-4, curve.msd.size)
            curves.append(MsdCurve(curve.lags, noisy, curve.pairs, curve.bins, 0.1, 2.0))
        summary = summarize_diffusion(curves, (0.3, 1.5))
        self.assertEqual(len(summary.per_run), 3)
        self.assertAlmostEqual(summary.plain.mean, 0.02, places=3)
        self.assertAlmostEqual(summary.plain.std, 0.002, places=3)
        self.assertAlmostEqual(summary.weighted.mean, 0.02, places=3)
        self.assertAlmostEqual(summary.pooled.coefficient, 0.02, places=3)

    def test_rejects_window_without_points(self) -> None:
        with self.assertRaises(ValueError):
            fit_diffusion(diffusive_curve(0.02, np.arange(3)), (5.0, 6.0))


if __name__ == "__main__":
    unittest.main()
