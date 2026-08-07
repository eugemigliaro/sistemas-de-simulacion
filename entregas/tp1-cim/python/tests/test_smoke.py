"""Pruebas mínimas del paquete de postproceso."""

import unittest

from tp1viz import __version__
from tp1viz.cli import build_parser


class SmokeTest(unittest.TestCase):
    def test_version_is_not_empty(self) -> None:
        self.assertTrue(__version__)

    def test_parser_has_expected_program_name(self) -> None:
        self.assertEqual(build_parser().prog, "tp1viz")


if __name__ == "__main__":
    unittest.main()
