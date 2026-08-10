"""Pruebas de lectura, validación y estadística de metrics-m.csv."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tp1viz.metrics import (
    REQUIRED_COLUMNS,
    Metric,
    MetricsError,
    read_metrics,
    summarize_metrics,
    write_summaries,
)


def metric(
    *,
    repetition: int,
    time_ns: int,
    particle_count: int = 100,
    cells_per_side: int = 2,
    method: str = "cim",
    neighbor_pairs: int = 7,
    distance_evaluations: int = 20,
    seed: int = 42,
) -> Metric:
    return Metric(
        seed=seed,
        boundary="walls",
        method=method,
        particle_count=particle_count,
        side=20.0,
        cells_per_side=cells_per_side,
        cutoff=1.0,
        repetition=repetition,
        time_ns=time_ns,
        neighbor_pairs=neighbor_pairs,
        distance_evaluations=distance_evaluations,
    )


def write_metrics(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def row(
    *,
    repetition: int,
    time_ns: int,
    particle_count: int = 100,
    cells_per_side: int = 2,
    method: str = "cim",
    neighbor_pairs: int = 7,
) -> dict[str, object]:
    return {
        "seed": 42,
        "boundary": "walls",
        "method": method,
        "N": particle_count,
        "L": 20,
        "M": cells_per_side,
        "rc": 1,
        "repetition": repetition,
        "time_ns": time_ns,
        "neighbor_pairs": neighbor_pairs,
        "distance_evaluations": 20,
    }


class SummaryTest(unittest.TestCase):
    def test_calculates_mean_and_population_standard_deviation(self) -> None:
        summaries = summarize_metrics(
            [
                metric(repetition=1, time_ns=1_000, distance_evaluations=10),
                metric(
                    repetition=2,
                    time_ns=3_000,
                    distance_evaluations=14,
                    seed=43,
                ),
            ]
        )

        self.assertEqual(len(summaries), 1)
        summary = summaries[0]
        self.assertEqual(summary.samples, 2)
        self.assertEqual(summary.seed_count, 2)
        self.assertEqual(summary.mean_time_ns, 2_000)
        self.assertEqual(summary.stddev_time_ns, 1_000)
        self.assertEqual(summary.mean_distance_evaluations, 12)
        self.assertEqual(summary.mean_neighbor_pairs, 7)

    def test_keeps_different_particle_counts_in_separate_groups(self) -> None:
        summaries = summarize_metrics(
            [
                metric(repetition=1, time_ns=100, particle_count=100),
                metric(repetition=2, time_ns=200, particle_count=100),
                metric(repetition=1, time_ns=300, particle_count=200),
                metric(repetition=2, time_ns=500, particle_count=200),
            ]
        )

        self.assertEqual(
            [summary.group.particle_count for summary in summaries],
            [100, 200],
        )

    def test_rejects_one_repetition(self) -> None:
        with self.assertRaisesRegex(MetricsError, "al menos dos repeticiones"):
            summarize_metrics([metric(repetition=1, time_ns=100)])

    def test_averages_changing_neighbor_count_between_seeds(self) -> None:
        summary = summarize_metrics(
            [
                metric(repetition=1, time_ns=100, neighbor_pairs=7, seed=42),
                metric(repetition=2, time_ns=200, neighbor_pairs=9, seed=43),
            ]
        )[0]
        self.assertEqual(summary.mean_neighbor_pairs, 8)
        self.assertEqual(summary.seed_count, 2)


class CsvTest(unittest.TestCase):
    def test_reads_and_writes_expected_columns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "metrics.csv"
            summary_path = root / "nested" / "summary.csv"
            write_metrics(
                source,
                [
                    row(repetition=1, time_ns=1_000),
                    row(repetition=2, time_ns=3_000),
                ],
            )

            summaries = summarize_metrics(read_metrics([source]))
            write_summaries(summary_path, summaries)

            with summary_path.open(newline="", encoding="utf-8") as input_file:
                output_rows = list(csv.DictReader(input_file))
            self.assertEqual(len(output_rows), 1)
            self.assertEqual(output_rows[0]["mean_time_ns"], "2000.000000")
            self.assertEqual(output_rows[0]["stddev_time_ns"], "1000.000000")
            self.assertEqual(output_rows[0]["samples"], "2")
            self.assertEqual(output_rows[0]["seed_count"], "1")

    def test_rejects_missing_columns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "metrics.csv"
            source.write_text("seed,N\n42,100\n", encoding="utf-8")

            with self.assertRaisesRegex(MetricsError, "faltan columnas"):
                read_metrics([source])

    def test_rejects_duplicate_repetition_across_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.csv"
            second = Path(directory) / "second.csv"
            write_metrics(first, [row(repetition=1, time_ns=100)])
            write_metrics(second, [row(repetition=1, time_ns=200)])

            with self.assertRaisesRegex(MetricsError, "duplicada"):
                read_metrics([first, second])

    def test_rejects_method_that_does_not_match_m(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "metrics.csv"
            write_metrics(
                source,
                [
                    row(
                        repetition=1,
                        time_ns=100,
                        cells_per_side=1,
                        method="cim",
                    )
                ],
            )

            with self.assertRaisesRegex(MetricsError, "M=1"):
                read_metrics([source])


if __name__ == "__main__":
    unittest.main()
