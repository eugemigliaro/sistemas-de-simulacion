from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tp2analysis.data import group_frames, read_observations, read_trajectory


class DataTests(unittest.TestCase):
    def test_reads_outputs_and_groups_frames(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            observations = root / "observations.csv"
            observations.write_text(
                "model,density,eta,seed,time,polarization,"
                "largest_cluster_fraction,cim_time_ns,neighbor_pairs,"
                "distance_evaluations\n"
                "vicsek,2,0.25,7,0,0.1,0.2,100,3,9\n",
                encoding="utf-8",
            )
            rows = read_observations(observations)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].seed, 7)

            trajectory = root / "trajectory.csv"
            trajectory.write_text(
                "model,density,eta,seed,time,id,x,y,vx,vy,angle\n"
                "vicsek,0.02,0,7,0,1,1,2,0.03,0,0\n"
                "vicsek,0.02,0,7,0,2,3,4,0,0.03,1.57079632679\n"
                "vicsek,0.02,0,7,1,1,1.03,2,0.03,0,0\n"
                "vicsek,0.02,0,7,1,2,3,4.03,0,0.03,1.57079632679\n",
                encoding="utf-8",
            )
            frames = group_frames(read_trajectory(trajectory))
            self.assertEqual(len(frames), 2)
            self.assertEqual(len(frames[0][1]), 2)


if __name__ == "__main__":
    unittest.main()
