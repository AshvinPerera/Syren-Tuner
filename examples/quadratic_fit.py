import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from syren_tuner import Parameter, ParameterSpace, Study
from syren_tuner.evaluators import CallableEvaluator
from syren_tuner.optimizers import RandomSearchOptimizer


def main() -> None:
    space = ParameterSpace(
        [
            Parameter("x", bounds=(-5.0, 5.0), initial=0.0),
            Parameter("y", bounds=(-5.0, 5.0), initial=0.0),
        ]
    )
    optimizer = RandomSearchOptimizer(space, max_evaluations=100, seed=11)
    study = Study(parameter_space=space, optimizer=optimizer)

    evaluator = CallableEvaluator(
        lambda trial: (trial.parameters["x"] - 1.5) ** 2
        + (trial.parameters["y"] + 2.0) ** 2
    )
    result = study.run(evaluator)

    print(f"status={result.status}")
    print(f"best_loss={result.best.loss if result.best else None}")
    print(f"best_parameters={result.best.trial.parameters if result.best else None}")


if __name__ == "__main__":
    main()
