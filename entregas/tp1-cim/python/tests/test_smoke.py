"""Pruebas mínimas del paquete de postproceso."""

import unittest

from tp1viz import __version__
from tp1viz.cli import build_parser


class SmokeTest(unittest.TestCase):
    def test_version_is_not_empty(self) -> None:
        self.assertTrue(__version__)

    def test_parser_has_expected_program_name(self) -> None:
        self.assertEqual(build_parser().prog, "tp1viz")

    def test_parser_accepts_plot_m(self) -> None:
        arguments = build_parser().parse_args(
            [
                "plot-m",
                "metrics.csv",
                "--summary",
                "summary.csv",
                "--figure",
                "time-vs-m.png",
            ]
        )
        self.assertEqual(arguments.command, "plot-m")

    def test_parser_accepts_plot_neighbors(self) -> None:
        arguments = build_parser().parse_args(
            [
                "plot-neighbors",
                "--static",
                "static.txt",
                "--dynamic",
                "dynamic.txt",
                "--neighbors",
                "neighbors.txt",
                "--particle",
                "7",
                "--figure",
                "neighbors.png",
            ]
        )
        self.assertEqual(arguments.command, "plot-neighbors")
        self.assertEqual(arguments.particle, 7)


if __name__ == "__main__":
    unittest.main()
