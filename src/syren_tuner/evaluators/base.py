"""Evaluator interfaces."""

from __future__ import annotations

from typing import Protocol

from syren_tuner.trials import Trial, TrialResult


class Evaluator(Protocol):
    """Protocol for local Python evaluations."""

    def evaluate(self, trial: Trial) -> float | TrialResult:
        """Evaluate a trial and return either a loss or a TrialResult."""

