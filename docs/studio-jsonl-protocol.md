# Studio JSONL Protocol

The Studio worker protocol is line-delimited JSON. Each message is one JSON
object followed by a newline.

Protocol version: `1`.

## Host Messages

### `start_study`

Starts or replaces the active study.

```json
{
  "type": "start_study",
  "study_id": "study_1",
  "optimizer": {
    "algorithm": "random_search",
    "max_evaluations": 25,
    "seed": 42
  },
  "parameters": [
    {
      "id": "tax_rate",
      "name": "Tax rate",
      "bounds": { "min": 0.0, "max": 1.0 },
      "initial": 0.2,
      "scale": "linear",
      "domain": { "kind": "continuous" }
    }
  ]
}
```

Supported algorithms:

- `random_search`
- `grid_search`
- `coordinate_search`
- `optuna`
- `scipy`

`optuna` and `scipy` require optional extras.

### `trial_result`

Returns the loss for the most recent candidate.

```json
{
  "type": "trial_result",
  "study_id": "study_1",
  "evaluation": 1,
  "loss": 0.125,
  "metadata": {
    "run_id": 41
  },
  "objective_breakdown": [],
  "diagnostics": []
}
```

### `cancel`

Cancels the active study.

```json
{
  "type": "cancel",
  "study_id": "study_1"
}
```

## Worker Events

### `ready`

Emitted after `start_study` is accepted.

```json
{
  "type": "ready",
  "study_id": "study_1",
  "protocol_version": 1
}
```

### `candidate`

Requests that Studio evaluate a candidate.

```json
{
  "type": "candidate",
  "study_id": "study_1",
  "evaluation": 1,
  "parameters": { "tax_rate": 0.2 },
  "max_evaluations": 25
}
```

### `progress`

Emitted after a `trial_result` is recorded.

```json
{
  "type": "progress",
  "study_id": "study_1",
  "evaluation": 1,
  "loss": 0.125,
  "best_loss": 0.125,
  "is_best": true,
  "evaluations_completed": 1,
  "max_evaluations": 25
}
```

### `completed`

Emitted when the study is completed or cancelled.

```json
{
  "type": "completed",
  "study_id": "study_1",
  "status": "completed",
  "evaluations_completed": 25,
  "best": {
    "evaluation": 4,
    "loss": 0.02,
    "parameters": { "tax_rate": 0.31 }
  }
}
```

### `error`

Emitted for protocol or optimization errors.

```json
{
  "type": "error",
  "study_id": "study_1",
  "code": "protocol_error",
  "message": "Missing required field 'loss'"
}
```

## Lifecycle

1. Studio starts `syren-tuner worker`.
2. Studio sends `start_study`.
3. Worker emits `ready` and the first `candidate`.
4. Studio evaluates the candidate and sends `trial_result`.
5. Worker emits `progress`, then either another `candidate` or `completed`.
6. Studio may send `cancel` at any time.

