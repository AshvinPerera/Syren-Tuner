import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from syren_tuner import Parameter, ParameterSpace, Study, StudyError, TrialResult
from syren_tuner.evaluators import CallableEvaluator
from syren_tuner.optimizers import RandomSearchOptimizer


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.space = ParameterSpace([Parameter("x", bounds=(-5.0, 5.0), initial=0.0)])

    def test_run_tracks_best_result(self):
        study = Study(
            self.space,
            RandomSearchOptimizer(self.space, max_evaluations=5, seed=3),
        )
        result = study.run(CallableEvaluator(lambda trial: (trial.parameters["x"] - 2.0) ** 2))
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.evaluations_completed, 5)
        self.assertIsNotNone(result.best)
        self.assertEqual(result.best.loss, min(trial.loss for trial in result.trials))

    def test_ask_requires_tell_before_next_trial(self):
        study = Study(self.space, RandomSearchOptimizer(self.space, max_evaluations=2, seed=1))
        study.ask()
        with self.assertRaises(StudyError):
            study.ask()

    def test_tell_records_pending_trial(self):
        study = Study(self.space, RandomSearchOptimizer(self.space, max_evaluations=1, seed=1))
        trial = study.ask()
        assert trial is not None
        study.tell(TrialResult(trial, loss=3.0))
        self.assertEqual(study.best_result.loss, 3.0)
        self.assertIsNone(study.ask())

    def test_cancel_stops_study(self):
        study = Study(self.space, RandomSearchOptimizer(self.space, max_evaluations=2, seed=1))
        study.cancel()
        self.assertIsNone(study.ask())
        self.assertEqual(study.result().status, "cancelled")


if __name__ == "__main__":
    unittest.main()

