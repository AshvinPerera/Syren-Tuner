"""Deterministic random search."""

from __future__ import annotations

from typing import Mapping, Sequence

from syren_tuner.optimizers.base import OptimizerBase
from syren_tuner.trials import TrialResult

MASK_64 = (1 << 64) - 1


class Lcg:
    """LCG matching Syren Studio's deterministic calibration RNG."""

    def __init__(self, seed: int) -> None:
        self.state = (int(seed) ^ 0x9E3779B97F4A7C15) & MASK_64

    def next_f64(self) -> float:
        self.state = (
            self.state * 6364136223846793005 + 1442695040888963407
        ) & MASK_64
        return (self.state >> 11) / float(1 << 53)


class RandomSearchOptimizer(OptimizerBase):
    """Initial candidate followed by deterministic random samples."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._rng = Lcg(self.seed)

    def ask(self, history: Sequence[TrialResult]) -> Mapping[str, float] | None:
        _ = history
        index = self._next_eval_index()
        if index is None:
            return None
        if index == 0:
            return self.parameter_space.initial()
        return {
            parameter.id: parameter.sample(self._rng.next_f64())
            for parameter in self.parameter_space
        }

