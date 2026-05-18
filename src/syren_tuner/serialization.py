"""Serialization helpers."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
import math
from typing import Any


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            return None
        return "inf" if value > 0 else "-inf"
    return value


def dumps(value: Any) -> str:
    return json.dumps(to_jsonable(value), separators=(",", ":"), sort_keys=True)


def loads(text: str) -> Any:
    return json.loads(text)

