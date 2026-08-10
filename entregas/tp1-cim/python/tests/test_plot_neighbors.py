"""Pruebas de la geometría visual periódica."""

import unittest

from tp1viz.plot_neighbors import periodic_image_centers


class PeriodicImagesTest(unittest.TestCase):
    def test_projects_across_edge_and_corner(self) -> None:
        images = {
            (round(x, 10), round(y, 10))
            for x, y in periodic_image_centers(0.1, 9.9, 0.25, 10.0)
        }
        self.assertEqual(
            images,
            {(10.1, 9.9), (0.1, -0.1), (10.1, -0.1)},
        )

    def test_does_not_project_interior_circle(self) -> None:
        self.assertEqual(periodic_image_centers(5.0, 5.0, 0.25, 10.0), [])


if __name__ == "__main__":
    unittest.main()
