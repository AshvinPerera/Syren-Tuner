"""Optional SciPy optimizer adapter."""

from __future__ import annotations

from typing import Mapping, Sequence

from syren_tuner.errors import OptionalDependencyError
from syren_tuner.optimizers.random_search import RandomSearchOptimizer
from syren_tuner.parameters import ParameterSpace
from syren_tuner.trials import TrialResult


class ScipyOptimizer(RandomSearchOptimizer):
    """Placeholder SciPy integration.

    V1 exposes the optional dependency gate and falls back to deterministic
    sampling semantics until a gradient-free SciPy method is wired to batched
    Syren evaluations.
    """

    def __init__(
        self,
        parameter_space: ParameterSpace,
        max_evaluations: int,
        seed: int | None = None,
    ) -> None:
        try:
            import scipy  # noqa: F401  # type: ignore
        except ImportError as exc:
            raise OptionalDependencyError("Install syren-tuner[scipy] to use SciPy") from exc
        super().__init__(parameter_space, max_evaluations, seed)

    def ask(self, history: Sequence[TrialResult]) -> Mapping[str, float] | None:
        return super().ask(history)

