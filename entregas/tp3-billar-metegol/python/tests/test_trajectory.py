from __future__ import annotations

import unittest

from support import still_rows, trajectory_text
from tp3analysis.trajectory import Obstacle, parse_trajectory


def simple_frames(final: bool = True):
    frames = [
        (0.0, 0, "initial", still_rows([0, 0])),
        (0.5, 3, "color", still_rows([1, 0])),
        (0.8, 5, "periodic", still_rows([1, 0])),
    ]
    if final:
        frames.append((2.0, 5, "final", still_rows([1, 0])))
    return frames


class TrajectoryTests(unittest.TestCase):
    def test_reads_header_and_frames(self) -> None:
        text = trajectory_text(
            simple_frames(), 2, seed=7, max_time=2.0, obstacles=[(0.6, 0.34, 0.05)]
        )
        trajectory = parse_trajectory(text)
        self.assertEqual(trajectory.header.seed, 7)
        self.assertEqual(trajectory.header.particle_count, 2)
        self.assertEqual(trajectory.header.obstacles, (Obstacle(0.6, 0.34, 0.05),))
        self.assertEqual(trajectory.header.max_time, 2.0)
        self.assertEqual(trajectory.positions.shape, (4, 2, 2))
        self.assertEqual(trajectory.reasons, ("initial", "color", "periodic", "final"))
        self.assertEqual(trajectory.states[1].tolist(), [1, 0])
        self.assertTrue(trajectory.complete)
        self.assertTrue(trajectory.reached_max_time)

    def test_final_before_max_time_means_event_cap(self) -> None:
        trajectory = parse_trajectory(trajectory_text(simple_frames(), 2, max_time=5.0))
        self.assertFalse(trajectory.reached_max_time)

    def test_without_max_time_the_ending_is_unknown(self) -> None:
        trajectory = parse_trajectory(trajectory_text(simple_frames(), 2))
        self.assertIsNone(trajectory.reached_max_time)

    def test_missing_final_frame_is_incomplete(self) -> None:
        trajectory = parse_trajectory(trajectory_text(simple_frames(final=False), 2))
        self.assertFalse(trajectory.complete)
        self.assertIsNone(trajectory.reached_max_time)

    def test_rejects_truncated_frame(self) -> None:
        text = trajectory_text(simple_frames(), 2)
        truncated = "\n".join(text.splitlines()[:-1]) + "\n"
        with self.assertRaisesRegex(ValueError, "incompleto"):
            parse_trajectory(truncated)

    def test_rejects_other_format(self) -> None:
        text = trajectory_text(simple_frames(), 2).replace("tp3-trajectory 1", "tp3-trajectory 2")
        with self.assertRaises(ValueError):
            parse_trajectory(text)

    def test_rejects_time_going_back(self) -> None:
        frames = simple_frames()
        frames[2] = (0.1, 5, "periodic", still_rows([1, 0]))
        with self.assertRaisesRegex(ValueError, "retroceden"):
            parse_trajectory(trajectory_text(frames, 2))

    def test_rejects_used_particle_turning_fresh(self) -> None:
        frames = simple_frames()
        frames[2] = (0.8, 5, "periodic", still_rows([0, 0]))
        with self.assertRaisesRegex(ValueError, "fresca"):
            parse_trajectory(trajectory_text(frames, 2))

    def test_rejects_frames_after_final(self) -> None:
        frames = simple_frames() + [(3.0, 6, "periodic", still_rows([1, 0]))]
        with self.assertRaisesRegex(ValueError, "después del final"):
            parse_trajectory(trajectory_text(frames, 2))

    def test_obstacle_count_must_match(self) -> None:
        text = trajectory_text(simple_frames(), 2).replace("# obstacle_count 0", "# obstacle_count 1")
        with self.assertRaisesRegex(ValueError, "obstacle_count"):
            parse_trajectory(text)

    def test_system_key_ignores_seed(self) -> None:
        first = parse_trajectory(trajectory_text(simple_frames(), 2, seed=1)).header
        second = parse_trajectory(trajectory_text(simple_frames(), 2, seed=2)).header
        with_obstacle = parse_trajectory(
            trajectory_text(simple_frames(), 2, seed=1, obstacles=[(0.6, 0.34, 0.05)])
        ).header
        self.assertEqual(first.system_key(), second.system_key())
        self.assertNotEqual(first.system_key(), with_obstacle.system_key())


if __name__ == "__main__":
    unittest.main()
