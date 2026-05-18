"""Trial data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Mapping


@dataclass(frozen=True, slots=True)
class Trial:
    """One candidate evaluation request."""

    number: int
    parameters: dict[str, float]
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "evaluation": self.number,
            "parameters": dict(self.parameters),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class TrialResult:
    """Completed candidate with a scalar loss."""

    trial: Trial
    loss: float
    metrics: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        loss = float(self.loss)
        if math.isnan(loss):
            loss = math.inf
        object.__setattr__(self, "loss", loss)

    @property
    def parameters(self) -> Mapping[str, float]:
        return self.trial.parameters

    def to_dict(self) -> dict[str, object]:
        return {
            "evaluation": self.trial.number,
            "loss": self.loss,
            "parameters": dict(self.trial.parameters),
            "metrics": dict(self.metrics),
            "metadata": dict(self.metadata),
            "diagnostics": list(self.diagnostics),
        }


@dataclass(frozen=True, slots=True)
class StudyResult:
    """Final or current study result."""

    status: str
    trials: list[TrialResult]
    best: TrialResult | None

    @property
    def evaluations_completed(self) -> int:
        return len(self.trials)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "evaluations_completed": self.evaluations_completed,
            "best": self.best.to_dict() if self.best else None,
            "trials": [trial.to_dict() for trial in self.trials],
        }

