"""Optimizer interfaces."""

from __future__ import annotations

from typing import Mapping, Protocol, Sequence

from syren_tuner.parameters import ParameterSpace
from syren_tuner.trials import TrialResult


class Optimizer(Protocol):
    """Protocol implemented by candidate generators."""

    @property
    def budget(self) -> int | None:
        """Expected number of evaluations, if finite."""

    def ask(self, history: Sequence[TrialResult]) -> Mapping[str, float] | None:
        """Return the next candidate or None when exhausted."""

    def tell(self, result: TrialResult) -> None:
        """Observe a completed trial."""


class OptimizerBase:
    """Base class for deterministic optimizers."""

    def __init__(
        self,
        parameter_space: ParameterSpace,
        max_evaluations: int,
        seed: int | None = None,
    ) -> None:
        if max_evaluations < 1:
            raise ValueError("max_evaluations must be >= 1")
        self.parameter_space = parameter_space
        self.max_evaluations = int(max_evaluations)
        self.seed = int(seed or 0)
        self._next_index = 0

    @property
    def budget(self) -> int:
        return self.max_evaluations

    def tell(self, result: TrialResult) -> None:
        _ = result

    def _next_eval_index(self) -> int | None:
        if self._next_index >= self.max_evaluations:
            return None
        index = self._next_index
        self._next_index += 1
        return index

