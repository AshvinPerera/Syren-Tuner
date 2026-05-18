"""Studio-facing JSONL worker."""

from __future__ import annotations

import sys
from typing import IO, Mapping

from syren_tuner.errors import ProtocolError, SyrenTunerError
from syren_tuner.optimizers import make_optimizer
from syren_tuner.parameters import ParameterSpace
from syren_tuner.protocol.jsonl import read_json_lines, write_json_line
from syren_tuner.protocol.messages import (
    PROTOCOL_VERSION,
    error_event,
    message_type,
    require_list,
    require_mapping,
    result_summary_event,
)
from syren_tuner.study import Study
from syren_tuner.trials import TrialResult


class StudioWorker:
    """Stateful worker for one active Studio tuning session."""

    def __init__(self, stdin: IO[str], stdout: IO[str]) -> None:
        self.stdin = stdin
        self.stdout = stdout
        self.study_id: str | None = None
        self.study: Study | None = None

    def run(self) -> int:
        for message in read_json_lines(self.stdin):
            try:
                self.handle(message)
            except SyrenTunerError as exc:
                self.emit(error_event(str(exc), self.study_id))
            except Exception as exc:  # Defensive: keep worker protocol-shaped.
                self.emit(error_event(str(exc), self.study_id, code="worker_error"))
        return 0

    def handle(self, message: Mapping[str, object]) -> None:
        kind = message_type(message)
        if kind == "start_study":
            self.start_study(message)
        elif kind == "trial_result":
            self.record_trial_result(message)
        elif kind == "cancel":
            self.cancel(message)
        else:
            raise ProtocolError(f"Unknown message type '{kind}'")

    def start_study(self, message: Mapping[str, object]) -> None:
        study_id = str(message.get("study_id") or "study")
        optimizer_config = require_mapping(message.get("optimizer"), "optimizer")
        parameter_values = require_list(message.get("parameters"), "parameters")
        parameters = [
            require_mapping(parameter, "parameters[]") for parameter in parameter_values
        ]
        space = ParameterSpace.from_dicts(parameters)
        algorithm = str(optimizer_config.get("algorithm") or "random_search")
        max_evaluations = int(optimizer_config.get("max_evaluations") or 1)
        seed_value = optimizer_config.get("seed")
        seed = int(seed_value) if seed_value is not None else None
        optimizer = make_optimizer(algorithm, space, max_evaluations, seed)
        self.study_id = study_id
        self.study = Study(space, optimizer, max_evaluations=max_evaluations)
        self.emit(
            {
                "type": "ready",
                "study_id": study_id,
                "protocol_version": PROTOCOL_VERSION,
            }
        )
        self.emit_next_candidate()

    def record_trial_result(self, message: Mapping[str, object]) -> None:
        study = self.require_study()
        pending = study.pending_trial
        if pending is None:
            raise ProtocolError("Received trial_result but no candidate is pending")
        evaluation = int(message.get("evaluation") or pending.number)
        if evaluation != pending.number:
            raise ProtocolError(
                f"trial_result evaluation {evaluation} does not match pending "
                f"candidate {pending.number}"
            )
        if "loss" not in message:
            raise ProtocolError("Missing required field 'loss'")
        metadata = dict(require_mapping(message.get("metadata") or {}, "metadata"))
        if "objective_breakdown" in message:
            metadata["objective_breakdown"] = message["objective_breakdown"]
        diagnostics = [str(item) for item in message.get("diagnostics") or []]
        result = TrialResult(
            trial=pending,
            loss=float(message["loss"]),
            metadata=metadata,
            diagnostics=diagnostics,
        )
        study.tell(result)
        best = study.best_result
        self.emit(
            {
                "type": "progress",
                "study_id": self.study_id,
                "evaluation": result.trial.number,
                "loss": result.loss,
                "best_loss": best.loss if best else None,
                "is_best": bool(best and best.trial.number == result.trial.number),
                "evaluations_completed": study.evaluations_completed,
                "max_evaluations": study.max_evaluations,
            }
        )
        self.emit_next_candidate()

    def cancel(self, message: Mapping[str, object]) -> None:
        _ = message
        study = self.require_study()
        study.cancel()
        self.emit(result_summary_event(self.study_id or "study", "cancelled", study.result()))

    def emit_next_candidate(self) -> None:
        study = self.require_study()
        trial = study.ask()
        if trial is None:
            self.emit(
                result_summary_event(
                    self.study_id or "study",
                    study.status,
                    study.result(),
                )
            )
            return
        self.emit(
            {
                "type": "candidate",
                "study_id": self.study_id,
                "evaluation": trial.number,
                "parameters": trial.parameters,
                "max_evaluations": study.max_evaluations,
            }
        )

    def require_study(self) -> Study:
        if self.study is None:
            raise ProtocolError("No active study; send start_study first")
        return self.study

    def emit(self, message: dict[str, object]) -> None:
        write_json_line(self.stdout, message)


def run_worker(stdin: IO[str] | None = None, stdout: IO[str] | None = None) -> int:
    return StudioWorker(stdin or sys.stdin, stdout or sys.stdout).run()

