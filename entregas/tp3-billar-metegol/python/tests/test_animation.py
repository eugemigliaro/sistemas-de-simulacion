from __future__ import annotations

import unittest

from support import still_rows, trajectory_text
import numpy as np

from tp3analysis.animation import event_frames_at, sampled_frames
from tp3analysis.trajectory import parse_trajectory


class AnimationTests(unittest.TestCase):
    def test_sampling_uses_real_non_final_frames(self) -> None:
        frames = [
            (0.0, 0, "initial", still_rows([0, 0])),
            (0.5, 3, "color", still_rows([1, 0])),
            (2.0, 5, "final", still_rows([1, 0])),
        ]
        trajectory = parse_trajectory(trajectory_text(frames, 2, max_time=2.0))
        selected = sampled_frames(trajectory, 2)
        self.assertEqual(selected.tolist(), [0, 1])
        self.assertNotIn("final", [trajectory.reasons[index] for index in selected])

    def test_real_time_uses_the_last_event_frame(self) -> None:
        frames = [
            (0.0, 0, "initial", still_rows([0, 0])),
            (0.5, 3, "color", still_rows([1, 0])),
            (1.2, 7, "periodic", still_rows([1, 0])),
            (2.0, 9, "final", still_rows([1, 0])),
        ]
        trajectory = parse_trajectory(trajectory_text(frames, 2, max_time=2.0))
        # Nunca se muestra el cuadro "final": es un avance hasta tmax.
        selected = event_frames_at(trajectory, np.array([0.0, 0.49, 0.5, 1.0, 1.9]))
        self.assertEqual(selected.tolist(), [0, 0, 1, 1, 2])

    def test_sampling_rejects_invalid_count(self) -> None:
        frames = [(0.0, 0, "initial", still_rows([0, 0]))]
        trajectory = parse_trajectory(trajectory_text(frames, 2))
        with self.assertRaisesRegex(ValueError, "positiva"):
            sampled_frames(trajectory, 0)


if __name__ == "__main__":
    unittest.main()
