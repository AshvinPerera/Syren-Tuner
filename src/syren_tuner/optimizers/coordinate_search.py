"""Coordinate search optimizer."""

from __future__ import annotations

from typing import Mapping, Sequence

from syren_tuner.optimizers.base import OptimizerBase
from syren_tuner.trials import TrialResult


class CoordinateSearchOptimizer(OptimizerBase):
    """Coordinate perturbation around the initial candidate."""

    def ask(self, history: Sequence[TrialResult]) -> Mapping[str, float] | None:
        _ = history
        index = self._next_eval_index()
        if index is None:
            return None
        initial = self.parameter_space.initial()
        if index == 0:
            return initial

        parameters = list(self.parameter_space)
        axis = (index - 1) % len(parameters)
        round_index = (index - 1) // len(parameters)
        direction = 1.0 if round_index % 2 == 0 else -1.0
        radius = 0.5 ** (round_index // 2 + 1)
        parameter = parameters[axis]
        value = initial[parameter.id] + direction * parameter.bounds.span * radius
        candidate = dict(initial)
        candidate[parameter.id] = parameter.normalize(value)
        return candidate

