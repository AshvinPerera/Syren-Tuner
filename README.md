# Syren Tuner

Syren Tuner is a Python optimization library for calibrating free parameters in
Syren agent-based models. It is intentionally a tuning layer: it proposes
candidate parameter values, receives scalar losses, tracks study state, and
reports progress.

Syren Studio remains responsible for compiling and running Rust simulators,
evaluating objective functions, and visualizing results.

## Install

From this checkout:

```powershell
python -m pip install -e .
```

Optional optimizer integrations are installed as extras:

```powershell
python -m pip install -e ".[optuna]"
python -m pip install -e ".[scipy]"
```

## Python API

```python
from syren_tuner import Parameter, ParameterSpace, Study
from syren_tuner.evaluators import CallableEvaluator
from syren_tuner.optimizers import RandomSearchOptimizer

space = ParameterSpace([
    Parameter("tax_rate", bounds=(0.0, 1.0), initial=0.2),
])

study = Study(
    parameter_space=space,
    optimizer=RandomSearchOptimizer(space, max_evaluations=25, seed=7),
)

result = study.run(
    CallableEvaluator(lambda trial: (trial.parameters["tax_rate"] - 0.32) ** 2)
)

print(result.best.loss, result.best.trial.parameters)
```

## Studio Worker

Studio can run Syren Tuner as a JSONL worker:

```powershell
syren-tuner worker
```

The worker reads host messages on stdin and emits events on stdout. Studio
evaluates each candidate against the compiled native runtime and sends the loss
back as a `trial_result` message.

See `docs/studio-jsonl-protocol.md` for the v1 protocol.

## Repository Layout

```text
src/syren_tuner/       Python package
tests/                 Unit and worker smoke tests
docs/                  Design and protocol notes
examples/              API and worker examples
```

## Status

This is an initial scaffold. V1 includes deterministic random search, grid
search, coordinate search, a local callable evaluator, and the Studio JSONL
worker. Native runtime loading from Python is intentionally deferred.

