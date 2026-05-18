"""Grid search optimizer."""

from __future__ import annotations

import math
from typing import Mapping, Sequence

from syren_tuner.optimizers.base import OptimizerBase
from syren_tuner.trials import TrialResult


class GridSearchOptimizer(OptimizerBase):
    """Cartesian grid traversal capped by max_evaluations."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._levels: int | None = None

    def ask(self, history: Sequence[TrialResult]) -> Mapping[str, float] | None:
        _ = history
        index = self._next_eval_index()
        if index is None:
            return None
        levels = self._grid_levels()
        n = index
        candidate: dict[str, float] = {}
        for parameter in self.parameter_space:
            level = n % levels
            n //= levels
            unit = 0.0 if levels == 1 else level / float(levels - 1)
            candidate[parameter.id] = parameter.sample(unit)
        return candidate

    def _grid_levels(self) -> int:
        if self._levels is None:
            self._levels = max(
                2,
                int(math.ceil(self.max_evaluations ** (1.0 / len(self.parameter_space)))),
            )
        return self._levels

