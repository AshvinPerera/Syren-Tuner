import importlib.util
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from syren_tuner import Parameter, ParameterSpace
from syren_tuner.optimizers import (
    CoordinateSearchOptimizer,
    GridSearchOptimizer,
    RandomSearchOptimizer,
)
from syren_tuner.optimizers.optuna_adapter import OptunaOptimizer
from syren_tuner.optimizers.scipy_adapter import ScipyOptimizer


def collect(optimizer):
    out = []
    history = []
    while True:
        candidate = optimizer.ask(history)
        if candidate is None:
            return out
        out.append(candidate)


class OptimizerTests(unittest.TestCase):
    def setUp(self):
        self.space = ParameterSpace(
            [
                Parameter("a", bounds=(0.0, 10.0), initial=5.0),
                Parameter("b", bounds=(0.0, 10.0), initial=5.0),
            ]
        )

    def test_random_search_is_deterministic(self):
        first = collect(RandomSearchOptimizer(self.space, max_evaluations=4, seed=42))
        second = collect(RandomSearchOptimizer(self.space, max_evaluations=4, seed=42))
        self.assertEqual(first, second)
        self.assertEqual(first[0], {"a": 5.0, "b": 5.0})

    def test_grid_search_sequence(self):
        values = collect(GridSearchOptimizer(self.space, max_evaluations=4, seed=1))
        self.assertEqual(
            values,
            [
                {"a": 0.0, "b": 0.0},
                {"a": 10.0, "b": 0.0},
                {"a": 0.0, "b": 10.0},
                {"a": 10.0, "b": 10.0},
            ],
        )

    def test_coordinate_search_sequence(self):
        values = collect(CoordinateSearchOptimizer(self.space, max_evaluations=5, seed=0))
        self.assertEqual(values[0], {"a": 5.0, "b": 5.0})
        self.assertEqual(values[1], {"a": 10.0, "b": 5.0})
        self.assertEqual(values[2], {"a": 5.0, "b": 10.0})
        self.assertEqual(values[3], {"a": 0.0, "b": 5.0})

    @unittest.skipIf(importlib.util.find_spec("optuna") is None, "optuna not installed")
    def test_optuna_adapter_imports_when_extra_is_available(self):
        optimizer = OptunaOptimizer(self.space, max_evaluations=1, seed=1)
        self.assertIsNotNone(optimizer.ask([]))

    @unittest.skipIf(importlib.util.find_spec("scipy") is None, "scipy not installed")
    def test_scipy_adapter_imports_when_extra_is_available(self):
        optimizer = ScipyOptimizer(self.space, max_evaluations=1, seed=1)
        self.assertIsNotNone(optimizer.ask([]))


if __name__ == "__main__":
    unittest.main()

