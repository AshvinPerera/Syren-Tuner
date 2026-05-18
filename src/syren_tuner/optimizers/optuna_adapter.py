"""Optional Optuna optimizer adapter."""

from __future__ import annotations

from typing import Mapping, Sequence

from syren_tuner.errors import OptionalDependencyError
from syren_tuner.optimizers.base import OptimizerBase
from syren_tuner.parameters import ParameterSpace
from syren_tuner.trials import TrialResult


class OptunaOptimizer(OptimizerBase):
    """Optuna-backed candidate generator.

    Install with `syren-tuner[optuna]`.
    """

    def __init__(
        self,
        parameter_space: ParameterSpace,
        max_evaluations: int,
        seed: int | None = None,
    ) -> None:
        super().__init__(parameter_space, max_evaluations, seed)
        try:
            import optuna  # type: ignore
        except ImportError as exc:
            raise OptionalDependencyError("Install syren-tuner[optuna] to use Optuna") from exc
        sampler = optuna.samplers.TPESampler(seed=self.seed)
        self._optuna = optuna
        self._study = optuna.create_study(direction="minimize", sampler=sampler)
        self._active_trial = None

    def ask(self, history: Sequence[TrialResult]) -> Mapping[str, float] | None:
        _ = history
        index = self._next_eval_index()
        if index is None:
            return None
        trial = self._study.ask()
        self._active_trial = trial
        candidate: dict[str, float] = {}
        for parameter in self.parameter_space:
            if parameter.domain == "integer":
                value = trial.suggest_int(
                    parameter.id,
                    int(parameter.bounds.min),
                    int(parameter.bounds.max),
                    log=parameter.scale == "log",
                )
            else:
                value = trial.suggest_float(
                    parameter.id,
                    parameter.bounds.min,
                    parameter.bounds.max,
                    log=parameter.scale == "log",
                )
            candidate[parameter.id] = parameter.normalize(float(value))
        return candidate

    def tell(self, result: TrialResult) -> None:
        if self._active_trial is not None:
            self._study.tell(self._active_trial, result.loss)
            self._active_trial = None

