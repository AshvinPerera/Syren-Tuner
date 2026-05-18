# Architecture

Syren Tuner is the optimization layer in the Syren toolchain.

```text
Syren Studio
  compiles project, owns runtime, evaluates objectives
        |
        | JSONL candidate/loss protocol
        v
Syren Tuner
  proposes candidates, tracks trials, reports progress
```

## Responsibilities

Syren Tuner owns:

- Parameter-space validation and candidate normalization.
- Optimizer implementations and optional adapter integrations.
- Study lifecycle, best-trial tracking, and cancellation state.
- A process protocol that lets Studio stream candidate evaluations.

Syren Tuner does not own:

- Rust compilation.
- Simulator loading or ABI management.
- Objective metric extraction from Syren snapshots.
- Studio UI state or project persistence.

## Core Concepts

- `Parameter` defines one tunable numeric value.
- `ParameterSpace` is an ordered, unique collection of parameters.
- `Trial` is one candidate assignment.
- `TrialResult` is a completed candidate with a scalar loss.
- `Optimizer` proposes candidates from prior results.
- `Study` coordinates optimizer state and records history.

## Extension Points

New optimizers should implement the `Optimizer` protocol or inherit
`OptimizerBase`. Optional third-party integrations should live behind extras so
the core package stays installable without compiled dependencies.

