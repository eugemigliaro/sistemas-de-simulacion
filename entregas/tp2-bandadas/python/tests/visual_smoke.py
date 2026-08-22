from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tp2analysis.animation import animate
from tp2analysis.data import Observation, ParticleState
from tp2analysis.plotting import (
    plot_eta,
    plot_polarization_vs_cluster,
    plot_time_series,
)
from tp2analysis.stats import Summary


class VisualizationSmokeTests(unittest.TestCase):
    def test_generates_valid_figures_and_animation(self) -> None:
        observations = [
            Observation("vicsek", 2.0, 0.25, 1, 0.0, 0.2, 0.8, 10, 2, 5),
            Observation("vicsek", 2.0, 0.25, 1, 1.0, 0.4, 0.9, 11, 3, 5),
        ]
        summaries = [
            Summary("vicsek", 2.0, 0.0, 2, 1.0, 0.9, 0.02, 1.0, 0.0, 10.0),
            Summary("vicsek", 2.0, 0.5, 2, 1.0, 0.4, 0.03, 0.9, 0.01, 11.0),
        ]
        states = [
            ParticleState("vicsek", 2.0, 0.25, 1, 0.0, 1, 1.0, 1.0, 0.03, 0.0, 0.0),
            ParticleState("vicsek", 2.0, 0.25, 1, 0.0, 2, 2.0, 2.0, 0.0, 0.03, 1.5708),
            ParticleState("vicsek", 2.0, 0.25, 1, 1.0, 1, 1.03, 1.0, 0.03, 0.0, 0.0),
            ParticleState("vicsek", 2.0, 0.25, 1, 1.0, 2, 2.0, 2.03, 0.0, 0.03, 1.5708),
        ]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outputs = [
                root / "timeseries.png",
                root / "polarization.png",
                root / "cluster.png",
                root / "va-s.png",
                root / "animation.gif",
            ]
            plot_time_series(observations, outputs[0], stationary_start=1.0)
            plot_eta(summaries, outputs[1], "polarization")
            plot_eta(summaries, outputs[2], "cluster")
            plot_polarization_vs_cluster(summaries, outputs[3])
            animate(states, observations, outputs[4], side=10.0, fps=2)

            for output in outputs:
                self.assertGreater(output.stat().st_size, 0)
                with Image.open(output) as image:
                    image.verify()
            with Image.open(outputs[4]) as animation:
                self.assertEqual(animation.n_frames, 2)
                self.assertEqual(animation.info.get("duration"), 500)


if __name__ == "__main__":
    unittest.main()
