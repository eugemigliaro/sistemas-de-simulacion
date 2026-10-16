from __future__ import annotations

import unittest

from tp3analysis.performance import parse_engine_report, summarize_performance


class EngineReportTests(unittest.TestCase):
    def test_parses_the_structured_summary_among_other_stderr_lines(self) -> None:
        report = parse_engine_report(
            "diagnóstico previo\n"
            "engine queue particles 100 seed 7 events 25226 frames 96 "
            "final_time 30 runtime_seconds 7.73757e-2\n"
            "aviso posterior\n"
        )
        self.assertEqual(report.engine, "queue")
        self.assertEqual(report.particle_count, 100)
        self.assertEqual(report.seed, 7)
        self.assertEqual(report.events, 25226)
        self.assertAlmostEqual(report.final_time, 30.0)
        self.assertAlmostEqual(report.runtime_seconds, 0.0773757)

    def test_rejects_missing_or_duplicated_summaries(self) -> None:
        with self.assertRaises(ValueError):
            parse_engine_report("sin resumen")
        summary = (
            "engine queue particles 10 seed 1 events 20 frames 3 "
            "final_time 30 runtime_seconds 0.1\n"
        )
        with self.assertRaises(ValueError):
            parse_engine_report(summary + summary)


class PerformanceSummaryTests(unittest.TestCase):
    def test_computes_mean_deviation_and_standard_error(self) -> None:
        rows = [
            {
                "engine": "queue",
                "particle_count": "10",
                "seed": "1",
                "max_time": "30",
                "runtime_seconds": "1",
                "events": "100",
                "frames": "11",
            },
            {
                "engine": "queue",
                "particle_count": "10",
                "seed": "2",
                "max_time": "30",
                "runtime_seconds": "3",
                "events": "120",
                "frames": "13",
            },
        ]
        summary = summarize_performance(rows)
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["repetitions"], "2")
        self.assertAlmostEqual(float(summary[0]["runtime_mean_s"]), 2.0)
        self.assertAlmostEqual(float(summary[0]["runtime_std_s"]), 2**0.5)
        self.assertAlmostEqual(float(summary[0]["runtime_sem_s"]), 1.0)
        self.assertAlmostEqual(float(summary[0]["events_mean"]), 110.0)

    def test_rejects_a_repeated_seed_within_one_group(self) -> None:
        row = {
            "engine": "queue",
            "particle_count": "10",
            "seed": "1",
            "max_time": "30",
            "runtime_seconds": "1",
            "events": "100",
            "frames": "11",
        }
        with self.assertRaises(ValueError):
            summarize_performance([row, row])


if __name__ == "__main__":
    unittest.main()
