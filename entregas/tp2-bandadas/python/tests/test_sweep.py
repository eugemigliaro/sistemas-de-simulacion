from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "run_sweep.py"
SPEC = importlib.util.spec_from_file_location("tp2_run_sweep", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
RUN_SWEEP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUN_SWEEP)


class SweepTests(unittest.TestCase):
    def test_only_reuses_complete_current_observation_csv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "observations.csv"
            output.write_text(
                ",".join(RUN_SWEEP.OBSERVATION_FIELDS)
                + "\n"
                + "vicsek,2,200,10,9,1,0.03,1,0.25,7,0,0.1,0.2,100,3,9\n"
                + "vicsek,2,200,10,9,1,0.03,1,0.25,7,1,0.2,0.3,110,4,10\n",
                encoding="utf-8",
            )
            parameters = {
                "model": "vicsek",
                "density": 2.0,
                "particle_count": 200,
                "side": 10.0,
                "cells": 9,
                "cutoff": 1.0,
                "speed": 0.03,
                "time_step": 1.0,
                "eta": 0.25,
                "seed": 7,
            }
            self.assertTrue(
                RUN_SWEEP.observations_are_complete(
                    output,
                    steps=1,
                    **parameters,
                )
            )
            self.assertFalse(
                RUN_SWEEP.observations_are_complete(
                    output,
                    steps=2,
                    **parameters,
                )
            )


if __name__ == "__main__":
    unittest.main()
