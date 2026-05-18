"""Syren Tuner public API."""

from syren_tuner.errors import (
    OptionalDependencyError,
    OptimizerError,
    ParameterError,
    ProtocolError,
    StudyError,
    SyrenTunerError,
)
from syren_tuner.parameters import Bounds, Parameter, ParameterSpace
from syren_tuner.study import Study
from syren_tuner.trials import StudyResult, Trial, TrialResult

__all__ = [
    "Bounds",
    "OptionalDependencyError",
    "OptimizerError",
    "Parameter",
    "ParameterError",
    "ParameterSpace",
    "ProtocolError",
    "Study",
    "StudyError",
    "StudyResult",
    "SyrenTunerError",
    "Trial",
    "TrialResult",
]

__version__ = "0.1.0"

