"""Study orchestration."""

from __future__ import annotations

from syren_tuner.evaluators.base import Evaluator
from syren_tuner.errors import StudyError
from syren_tuner.optimizers.base import Optimizer
from syren_tuner.parameters import ParameterSpace
from syren_tuner.trials import StudyResult, Trial, TrialResult


class Study:
    """Coordinates optimizer candidate generation and result tracking."""

    def __init__(
        self,
        parameter_space: ParameterSpace,
        optimizer: Optimizer,
        max_evaluations: int | None = None,
    ) -> None:
        self.parameter_space = parameter_space
        self.optimizer = optimizer
        self.max_evaluations = max_evaluations or optimizer.budget
        self._history: list[TrialResult] = []
        self._pending: Trial | None = None
        self._best: TrialResult | None = None
        self._status = "idle"

    @property
    def status(self) -> str:
        return self._status

    @property
    def history(self) -> tuple[TrialResult, ...]:
        return tuple(self._history)

    @property
    def best_result(self) -> TrialResult | None:
        return self._best

    @property
    def pending_trial(self) -> Trial | None:
        return self._pending

    @property
    def evaluations_completed(self) -> int:
        return len(self._history)

    def ask(self) -> Trial | None:
        if self._status == "cancelled":
            return None
        if self._pending is not None:
            raise StudyError("Cannot ask for a new trial while one is pending")
        if self.max_evaluations is not None and len(self._history) >= self.max_evaluations:
            self._status = "completed"
            return None
        candidate = self.optimizer.ask(self.history)
        if candidate is None:
            self._status = "completed"
            return None
        trial = Trial(
            number=len(self._history) + 1,
            parameters=self.parameter_space.clamp(candidate),
        )
        self._pending = trial
        self._status = "running"
        return trial

    def tell(self, result: TrialResult) -> TrialResult:
        if self._pending is None:
            raise StudyError("Cannot tell a result when no trial is pending")
        if result.trial.number != self._pending.number:
            raise StudyError(
                f"Result evaluation {result.trial.number} does not match pending "
                f"evaluation {self._pending.number}"
            )
        self._history.append(result)
        self.optimizer.tell(result)
        if self._best is None or result.loss < self._best.loss:
            self._best = result
        self._pending = None
        if self.max_evaluations is not None and len(self._history) >= self.max_evaluations:
            self._status = "completed"
        return result

    def cancel(self) -> None:
        self._pending = None
        self._status = "cancelled"

    def result(self) -> StudyResult:
        return StudyResult(status=self._status, trials=list(self._history), best=self._best)

    def run(self, evaluator: Evaluator) -> StudyResult:
        while True:
            trial = self.ask()
            if trial is None:
                break
            evaluated = evaluator.evaluate(trial)
            if isinstance(evaluated, TrialResult):
                result = evaluated
            else:
                result = TrialResult(trial=trial, loss=float(evaluated))
            self.tell(result)
        return self.result()

