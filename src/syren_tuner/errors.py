"""Exception hierarchy for Syren Tuner."""


class SyrenTunerError(Exception):
    """Base class for Syren Tuner errors."""


class ParameterError(SyrenTunerError, ValueError):
    """Raised when a parameter space is invalid."""


class OptimizerError(SyrenTunerError):
    """Raised when an optimizer cannot produce or accept a trial."""


class StudyError(SyrenTunerError):
    """Raised when a study lifecycle operation is invalid."""


class ProtocolError(SyrenTunerError):
    """Raised when JSONL worker protocol data is invalid."""


class WorkerError(SyrenTunerError):
    """Raised when the Studio worker cannot continue."""


class OptionalDependencyError(SyrenTunerError, ImportError):
    """Raised when an optional optimizer integration is unavailable."""

