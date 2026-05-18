"""Parameter-space definitions and sampling helpers."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Iterator, Mapping, Sequence

from syren_tuner.errors import ParameterError

Scale = str
Domain = str


@dataclass(frozen=True, slots=True)
class Bounds:
    """Closed numeric bounds for a parameter."""

    min: float
    max: float

    def __post_init__(self) -> None:
        lo = float(self.min)
        hi = float(self.max)
        if not math.isfinite(lo) or not math.isfinite(hi):
            raise ParameterError("Parameter bounds must be finite")
        if lo > hi:
            raise ParameterError("Parameter lower bound must be <= upper bound")
        object.__setattr__(self, "min", lo)
        object.__setattr__(self, "max", hi)

    @property
    def span(self) -> float:
        return self.max - self.min

    def clamp(self, value: float) -> float:
        value = float(value)
        if math.isnan(value):
            return self.min
        return min(max(value, self.min), self.max)

    def to_dict(self) -> dict[str, float]:
        return {"min": self.min, "max": self.max}


@dataclass(frozen=True, slots=True)
class Parameter:
    """One tunable numeric free parameter."""

    id: str
    bounds: Bounds | tuple[float, float] | Mapping[str, float]
    initial: float | None = None
    scale: Scale = "linear"
    domain: Domain | Mapping[str, str] | None = "continuous"
    name: str | None = None

    def __post_init__(self) -> None:
        ident = self.id.strip()
        if not ident:
            raise ParameterError("Parameter id must not be empty")
        bounds = coerce_bounds(self.bounds)
        scale = normalize_scale(self.scale)
        domain = normalize_domain(self.domain)
        if scale == "log" and (bounds.min <= 0.0 or bounds.max <= 0.0):
            raise ParameterError("Log-scaled parameters require positive bounds")
        initial = bounds.min if self.initial is None else float(self.initial)
        initial = snap_to_domain(bounds.clamp(initial), domain)
        object.__setattr__(self, "id", ident)
        object.__setattr__(self, "bounds", bounds)
        object.__setattr__(self, "scale", scale)
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "initial", initial)
        object.__setattr__(self, "name", self.name or ident)

    def sample(self, unit: float) -> float:
        """Sample this parameter from a unit value in [0, 1]."""

        unit = min(max(float(unit), 0.0), 1.0)
        if self.scale == "log":
            lo = math.log(self.bounds.min)
            hi = math.log(self.bounds.max)
            value = math.exp(lo + (hi - lo) * unit)
        else:
            value = self.bounds.min + self.bounds.span * unit
        return self.normalize(value)

    def normalize(self, value: float) -> float:
        return snap_to_domain(self.bounds.clamp(float(value)), self.domain)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "bounds": self.bounds.to_dict(),
            "initial": self.initial,
            "scale": self.scale,
            "domain": {"kind": self.domain},
        }


class ParameterSpace:
    """Ordered collection of unique parameters."""

    def __init__(self, parameters: Iterable[Parameter]) -> None:
        items = tuple(parameters)
        if not items:
            raise ParameterError("ParameterSpace requires at least one parameter")
        seen: set[str] = set()
        for parameter in items:
            if parameter.id in seen:
                raise ParameterError(f"Duplicate parameter id '{parameter.id}'")
            seen.add(parameter.id)
        self._parameters = items
        self._by_id = {parameter.id: parameter for parameter in items}

    def __iter__(self) -> Iterator[Parameter]:
        return iter(self._parameters)

    def __len__(self) -> int:
        return len(self._parameters)

    def __getitem__(self, parameter_id: str) -> Parameter:
        try:
            return self._by_id[parameter_id]
        except KeyError as exc:
            raise ParameterError(f"Unknown parameter id '{parameter_id}'") from exc

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(parameter.id for parameter in self._parameters)

    def initial(self) -> dict[str, float]:
        return {parameter.id: parameter.initial for parameter in self._parameters}

    def sample(self, units: Sequence[float]) -> dict[str, float]:
        if len(units) != len(self._parameters):
            raise ParameterError("Unit vector length must match parameter count")
        return {
            parameter.id: parameter.sample(unit)
            for parameter, unit in zip(self._parameters, units, strict=True)
        }

    def clamp(self, candidate: Mapping[str, float]) -> dict[str, float]:
        missing = [parameter.id for parameter in self._parameters if parameter.id not in candidate]
        if missing:
            raise ParameterError(f"Candidate is missing parameters: {', '.join(missing)}")
        return {
            parameter.id: parameter.normalize(float(candidate[parameter.id]))
            for parameter in self._parameters
        }

    def to_list(self) -> list[dict[str, object]]:
        return [parameter.to_dict() for parameter in self._parameters]

    @classmethod
    def from_dicts(cls, values: Iterable[Mapping[str, object]]) -> ParameterSpace:
        return cls(parameter_from_dict(value) for value in values)


def parameter_from_dict(value: Mapping[str, object]) -> Parameter:
    try:
        ident = str(value["id"])
        bounds = value["bounds"]
    except KeyError as exc:
        raise ParameterError(f"Missing parameter field '{exc.args[0]}'") from exc
    return Parameter(
        id=ident,
        name=str(value.get("name") or ident),
        bounds=coerce_bounds(bounds),
        initial=float(value["initial"]) if value.get("initial") is not None else None,
        scale=str(value.get("scale") or "linear"),
        domain=value.get("domain") or "continuous",
    )


def coerce_bounds(value: Bounds | tuple[float, float] | Mapping[str, float] | object) -> Bounds:
    if isinstance(value, Bounds):
        return value
    if isinstance(value, Mapping):
        return Bounds(float(value["min"]), float(value["max"]))
    if isinstance(value, tuple) and len(value) == 2:
        return Bounds(float(value[0]), float(value[1]))
    raise ParameterError("Bounds must be a Bounds object, mapping, or (min, max) tuple")


def normalize_scale(value: object) -> Scale:
    scale = str(value or "linear").lower()
    if scale not in {"linear", "log"}:
        raise ParameterError(f"Unsupported parameter scale '{scale}'")
    return scale


def normalize_domain(value: object) -> Domain:
    if value is None:
        return "continuous"
    if isinstance(value, Mapping):
        value = value.get("kind", "continuous")
    domain = str(value).lower()
    if domain not in {"continuous", "integer"}:
        raise ParameterError(f"Unsupported parameter domain '{domain}'")
    return domain


def snap_to_domain(value: float, domain: Domain) -> float:
    if domain == "integer":
        return float(round_half_away_from_zero(value))
    return float(value)


def round_half_away_from_zero(value: float) -> int:
    """Match Rust f64::round semantics for halfway cases."""

    if value >= 0.0:
        return math.floor(value + 0.5)
    return math.ceil(value - 0.5)
