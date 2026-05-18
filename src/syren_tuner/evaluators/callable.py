"""Callable evaluator wrapper."""

from __future__ import annotations

from collections.abc import Callable

from syren_tuner.trials import Trial, TrialResult


class CallableEvaluator:
    """Wrap a Python callable as an evaluator."""

    def __init__(self, function: Callable[[Trial], float | TrialResult]) -> None:
        self.function = function

    def evaluate(self, trial: Trial) -> float | TrialResult:
        return self.function(trial)

