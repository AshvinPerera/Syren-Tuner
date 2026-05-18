import json
import os
import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CliWorkerTests(unittest.TestCase):
    def test_worker_smoke_session(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        input_text = "\n".join(
            [
                json.dumps(
                    {
                        "type": "start_study",
                        "study_id": "smoke",
                        "optimizer": {
                            "algorithm": "random_search",
                            "max_evaluations": 2,
                            "seed": 5,
                        },
                        "parameters": [
                            {
                                "id": "x",
                                "bounds": {"min": 0.0, "max": 1.0},
                                "initial": 0.5,
                                "scale": "linear",
                                "domain": {"kind": "continuous"},
                            }
                        ],
                    }
                ),
                json.dumps(
                    {
                        "type": "trial_result",
                        "study_id": "smoke",
                        "evaluation": 1,
                        "loss": 1.0,
                    }
                ),
                json.dumps(
                    {
                        "type": "trial_result",
                        "study_id": "smoke",
                        "evaluation": 2,
                        "loss": 0.25,
                    }
                ),
                "",
            ]
        )
        proc = subprocess.run(
            [sys.executable, "-m", "syren_tuner.cli", "worker"],
            cwd=ROOT,
            env=env,
            input=input_text,
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
        events = [json.loads(line) for line in proc.stdout.splitlines()]
        self.assertEqual(events[0]["type"], "ready")
        self.assertEqual([event["type"] for event in events].count("candidate"), 2)
        self.assertEqual(events[-1]["type"], "completed")
        self.assertEqual(events[-1]["status"], "completed")
        self.assertEqual(events[-1]["best"]["loss"], 0.25)


if __name__ == "__main__":
    unittest.main()

