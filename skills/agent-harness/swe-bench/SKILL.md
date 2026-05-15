---
name: swe-bench
description: "SWE-bench: benchmark for evaluating AI coding agents on real GitHub issues."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [git, docker]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [SWE-bench, Benchmark, Coding Agent, GitHub Issues, Software Engineering, Evaluation]
---

# SWE-bench: Software Engineering Benchmark

## What's inside

Evaluate AI coding agents on real GitHub issues. The standard benchmark for measuring how well agents can fix bugs, implement features, and resolve issues in real codebases.

## Quick start

**Install**:
```bash
pip install swebench
```

**Run evaluation**:
```bash
python -m swebench.harness.run_evaluation \
  --predictions_path predictions.json \
  --max_workers 4 \
  --run_id test_run
```

## Common workflows

### Workflow 1: Prepare Predictions

```python
import json

# Format predictions
predictions = [
    {
        "instance_id": "django__django-1234",
        "model_patch": "diff --git a/django/...",
        "model_name_or_path": "my-agent"
    }
]

with open("predictions.json", "w") as f:
    json.dump(predictions, f)
```

### Workflow 2: Run Evaluation

```bash
# Download dataset
python -m swebench.dataset.download

# Run evaluation
python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Lite \
  --predictions_path predictions.json \
  --max_workers 4 \
  --run_id my_run
```

### Workflow 3: Analyze Results

```python
from swebench.metrics import get_metrics

results = get_metrics("results/my_run.json")
print(f"Resolved: {results['resolved']}/{results['total']}")
print(f"Accuracy: {results['accuracy']:.2%}")
```

## Benchmark Variants

| Variant | Issues | Difficulty | Use Case |
|---------|--------|------------|----------|
| SWE-bench Lite | 300 | Easy-Medium | Quick evaluation |
| SWE-bench Full | 2,294 | All | Comprehensive |
| SWE-bench Verified | 500 | Verified | Reproducible |

## Common issues

**Issue: Docker fails**
- Ensure Docker daemon is running
- Check disk space
- Use `--max_workers 1` for debugging

**Issue: Patch not applied**
- Verify patch format
- Check file paths
- Ensure clean git state

## Resources

- GitHub: https://github.com/SWE-bench/SWE-bench
- Dataset: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite
