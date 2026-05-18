"""Optimizer implementations."""

from syren_tuner.errors import OptimizerError
from syren_tuner.optimizers.base import Optimizer, OptimizerBase
from syren_tuner.optimizers.coordinate_search import CoordinateSearchOptimizer
from syren_tuner.optimizers.grid_search import GridSearchOptimizer
from syren_tuner.optimizers.random_search import RandomSearchOptimizer
from syren_tuner.parameters import ParameterSpace

__all__ = [
    "CoordinateSearchOptimizer",
    "GridSearchOptimizer",
    "Optimizer",
    "OptimizerBase",
    "RandomSearchOptimizer",
    "make_optimizer",
]


def make_optimizer(
    algorithm: str,
    parameter_space: ParameterSpace,
    max_evaluations: int,
    seed: int | None = None,
):
    name = algorithm.strip().lower().replace("-", "_")
    if name == "random_search":
        return RandomSearchOptimizer(parameter_space, max_evaluations, seed)
    if name == "grid_search":
        return GridSearchOptimizer(parameter_space, max_evaluations, seed)
    if name == "coordinate_search":
        return CoordinateSearchOptimizer(parameter_space, max_evaluations, seed)
    if name == "optuna":
        from syren_tuner.optimizers.optuna_adapter import OptunaOptimizer

        return OptunaOptimizer(parameter_space, max_evaluations, seed)
    if name == "scipy":
        from syren_tuner.optimizers.scipy_adapter import ScipyOptimizer

        return ScipyOptimizer(parameter_space, max_evaluations, seed)
    raise OptimizerError(f"Unsupported optimizer algorithm '{algorithm}'")

