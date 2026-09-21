from __future__ import annotations

import math
import unittest

import numpy as np

from tp3analysis.fit import fit_through_origin, sum_squared_error
from tp3analysis.stats import describe, weighted_mean


class FitTests(unittest.TestCase):
    def test_exact_line_through_origin(self) -> None:
        x = np.linspace(0.1, 2.0, 20)
        fit = fit_through_origin(x, 3.0 * x)
        self.assertAlmostEqual(fit.slope, 3.0, places=10)
        self.assertAlmostEqual(fit.residual, 0.0, places=15)
        self.assertLess(fit.slope_error, 1e-8)

    def test_sweep_agrees_with_closed_form(self) -> None:
        # La fórmula cerrada solo se usa acá, como control del barrido.
        rng = np.random.default_rng(3)
        x = np.linspace(0.3, 1.5, 60)
        y = 0.09 * x + rng.normal(0, 0.002, x.size)
        fit = fit_through_origin(x, y)
        closed = float(np.sum(x * y) / np.sum(x * x))
        # E(c) es plana cerca del mínimo: el barrido lo ubica con una
        # precisión muy inferior a la incertidumbre del ajuste, no al bit.
        self.assertLess(abs(fit.slope - closed), 1e-6 * fit.slope_error)
        expected_error = math.sqrt(fit.residual / (x.size - 1) / np.sum(x * x))
        self.assertAlmostEqual(fit.slope_error, expected_error, places=15)

    def test_sweep_grid_contains_the_minimum(self) -> None:
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([2.1, 3.9, 6.2])
        fit = fit_through_origin(x, y)
        self.assertGreater(fit.slope, fit.sweep_c[0])
        self.assertLess(fit.slope, fit.sweep_c[-1])
        # El mínimo refinado no es peor que ningún punto de la grilla.
        self.assertLessEqual(fit.residual, float(fit.sweep_error.min()) + 1e-15)
        self.assertAlmostEqual(
            float(sum_squared_error(x, y, fit.slope)[0]), fit.residual, places=15
        )

    def test_error_shrinks_with_less_noise(self) -> None:
        rng = np.random.default_rng(5)
        x = np.linspace(0.3, 1.5, 60)
        noise = rng.normal(0, 1, x.size)
        noisy = fit_through_origin(x, 0.09 * x + 0.01 * noise)
        clean = fit_through_origin(x, 0.09 * x + 0.001 * noise)
        self.assertLess(clean.slope_error, noisy.slope_error)

    def test_rejects_non_positive_x(self) -> None:
        with self.assertRaises(ValueError):
            fit_through_origin(np.array([0.0, 1.0]), np.array([0.0, 1.0]))


class StatsTests(unittest.TestCase):
    def test_describe(self) -> None:
        estimate = describe([1.0, 2.0, 3.0, 4.0])
        self.assertAlmostEqual(estimate.mean, 2.5)
        self.assertAlmostEqual(estimate.std, math.sqrt(5 / 3))
        self.assertAlmostEqual(estimate.sem, math.sqrt(5 / 3) / 2)
        self.assertEqual(estimate.count, 4)

    def test_single_value_has_no_dispersion(self) -> None:
        estimate = describe([2.0])
        self.assertTrue(math.isnan(estimate.std))
        self.assertTrue(math.isnan(estimate.sem))

    def test_weighted_mean_favors_precise_values(self) -> None:
        result = weighted_mean([1.0, 3.0], [0.1, 1.0])
        self.assertAlmostEqual(result.mean, (1 / 0.01 + 3 / 1) / (1 / 0.01 + 1))
        self.assertAlmostEqual(result.error, 1 / math.sqrt(100 + 1))

    def test_equal_errors_give_plain_mean_and_sigma_over_sqrt_n(self) -> None:
        result = weighted_mean([1.0, 2.0, 3.0, 4.0], [0.2] * 4)
        self.assertAlmostEqual(result.mean, 2.5)
        self.assertAlmostEqual(result.error, 0.1)

    def test_weighted_mean_rejects_zero_error(self) -> None:
        with self.assertRaises(ValueError):
            weighted_mean([1.0, 2.0], [0.1, 0.0])


if __name__ == "__main__":
    unittest.main()
