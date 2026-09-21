from __future__ import annotations

import unittest

from support import still_rows, trajectory_text
from tp3analysis.goals import goal_curve, threshold_goals, time_to_fraction
from tp3analysis.trajectory import parse_trajectory


def ten_particles(goal_times: list[float], end: float = 10.0, final: bool = True, max_time=None):
    """Diez partículas; la i-ésima hace gol en goal_times[i]."""
    states = [0] * 10
    frames = [(0.0, 0, "initial", still_rows(states))]
    events = 0
    for index, time in enumerate(goal_times):
        events += 3
        # Un cuadro periódico entre goles no debe mover Ng.
        frames.append((time - 0.01, events - 1, "periodic", still_rows(states)))
        states[index] = 1
        frames.append((time, events, "color", still_rows(states)))
    if final:
        frames.append((end, events, "final", still_rows(states)))
    return parse_trajectory(trajectory_text(frames, 10, max_time=max_time))


class GoalTests(unittest.TestCase):
    def test_threshold_does_not_depend_on_rounding(self) -> None:
        self.assertEqual(threshold_goals(100, 0.9), 90)
        self.assertEqual(threshold_goals(10, 0.9), 9)
        self.assertEqual(threshold_goals(7, 0.9), 7)

    def test_goal_curve_steps_at_color_frames(self) -> None:
        curve = goal_curve(ten_particles([1.0, 2.0, 3.5]))
        self.assertEqual(curve.times.tolist(), [0.0, 1.0, 2.0, 3.5])
        self.assertEqual(curve.goals.tolist(), [0, 1, 2, 3])
        self.assertAlmostEqual(curve.used_fraction[-1], 0.3)
        self.assertEqual(curve.end_time, 10.0)

    def test_t90_is_the_exact_time_of_the_ninth_goal(self) -> None:
        times = [0.5 * (i + 1) for i in range(10)]
        result = time_to_fraction(ten_particles(times, max_time=10.0))
        self.assertTrue(result.reached)
        self.assertEqual(result.threshold_goals, 9)
        self.assertEqual(result.t90, 4.5)
        self.assertEqual(result.goals_at_end, 10)
        self.assertEqual(result.ended_by, "max_time")

    def test_not_reached_is_reported_with_goals_at_end(self) -> None:
        result = time_to_fraction(ten_particles([1.0, 2.0], max_time=10.0))
        self.assertFalse(result.reached)
        self.assertIsNone(result.t90)
        self.assertEqual(result.goals_at_end, 2)
        self.assertEqual(result.final_time, 10.0)

    def test_event_cap_is_distinguished_from_tmax(self) -> None:
        result = time_to_fraction(ten_particles([1.0], end=4.0, max_time=10.0))
        self.assertEqual(result.ended_by, "max_events")

    def test_truncated_file_without_threshold_is_an_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "truncado"):
            time_to_fraction(ten_particles([1.0, 2.0], final=False))

    def test_truncated_file_after_threshold_still_gives_t90(self) -> None:
        times = [0.5 * (i + 1) for i in range(9)]
        result = time_to_fraction(ten_particles(times, final=False))
        self.assertEqual(result.t90, 4.5)

    def test_goal_without_color_frame_is_rejected(self) -> None:
        frames = [
            (0.0, 0, "initial", still_rows([0, 0])),
            (1.0, 4, "periodic", still_rows([1, 0])),
            (2.0, 4, "final", still_rows([1, 0])),
        ]
        trajectory = parse_trajectory(trajectory_text(frames, 2))
        with self.assertRaisesRegex(ValueError, "cuadro de color"):
            goal_curve(trajectory)


if __name__ == "__main__":
    unittest.main()
