"""JSONL protocol message helpers."""

from __future__ import annotations

from typing import Mapping

from syren_tuner.errors import ProtocolError

PROTOCOL_VERSION = 1


def message_type(message: Mapping[str, object]) -> str:
    kind = message.get("type")
    if not isinstance(kind, str) or not kind:
        raise ProtocolError("Message must include a non-empty 'type'")
    return kind


def require_mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ProtocolError(f"Field '{field}' must be an object")
    return value


def require_list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise ProtocolError(f"Field '{field}' must be a list")
    return value


def error_event(
    message: str,
    study_id: str | None = None,
    code: str = "protocol_error",
) -> dict[str, object]:
    event: dict[str, object] = {
        "type": "error",
        "code": code,
        "message": message,
    }
    if study_id is not None:
        event["study_id"] = study_id
    return event


def result_summary_event(study_id: str, status: str, result) -> dict[str, object]:
    best = result.best
    return {
        "type": "completed",
        "study_id": study_id,
        "status": status,
        "evaluations_completed": result.evaluations_completed,
        "best": best.to_dict() if best else None,
    }

