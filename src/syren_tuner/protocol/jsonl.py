"""Line-delimited JSON I/O."""

from __future__ import annotations

import json
from typing import IO, Iterator

from syren_tuner.errors import ProtocolError
from syren_tuner.serialization import to_jsonable


def parse_json_line(line: str) -> dict[str, object]:
    try:
        value = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"Invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ProtocolError("JSONL messages must be objects")
    return value


def read_json_lines(stream: IO[str]) -> Iterator[dict[str, object]]:
    for line in stream:
        if not line.strip():
            continue
        yield parse_json_line(line)


def write_json_line(stream: IO[str], message: dict[str, object]) -> None:
    json.dump(to_jsonable(message), stream, separators=(",", ":"))
    stream.write("\n")
    stream.flush()

