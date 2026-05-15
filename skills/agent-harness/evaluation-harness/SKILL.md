---
name: evaluation-harness
description: "Comprehensive evaluation harness for AI agents: benchmark management, regression testing, and performance tracking across multiple evaluation frameworks."
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Evaluation, Benchmark, Regression, Performance, Harness, Testing, Metrics]
---

# Evaluation Harness for Agents

## What's inside

Comprehensive evaluation harness: benchmark management, regression testing, performance tracking, and comparison across multiple frameworks.

## Quick start

```python
from evaluation_harness import EvaluationHarness

# Create harness
harness = EvaluationHarness()

# Add benchmarks
harness.add_benchmark("mmlu", MMLUBenchmark())
harness.add_benchmark("humaneval", HumanEvalBenchmark())

# Run evaluation
results = harness.run(model="gpt-4")

# Compare with baseline
comparison = harness.compare(results, baseline="baseline.json")
print(comparison.improved)
print(comparison.regressed)
```

## Common workflows

### Workflow 1: Run Benchmark Suite

```python
suite = BenchmarkSuite([
    MMLUBenchmark(),
    GSM8KBenchmark(),
    HumanEvalBenchmark(),
])

results = suite.run(model="my-model")
suite.save_results(results, "results.json")
```

### Workflow 2: Regression Testing

```python
regression = RegressionTester(baseline="baseline.json")

new_results = suite.run(model="my-model-v2")
report = regression.compare(new_results)

if report.has_regressions:
    print("Regressions detected!")
    for r in report.regressions:
        print(f"  {r.benchmark}: {r.old_score} -> {r.new_score}")
```

### Workflow 3: Performance Tracking

```python
tracker = PerformanceTracker()

tracker.record("v1.0", results_v1)
tracker.record("v1.1", results_v2)
tracker.record("v1.2", results_v3)

tracker.plot_trends("trends.png")
```

## Benchmark Types

| Type | Examples | Metrics |
|------|----------|---------|
| Knowledge | MMLU, ARC | Accuracy |
| Reasoning | GSM8K, BBH | Exact match |
| Code | HumanEval, MBPP | Pass@k |
| Safety | TruthfulQA | Accuracy |
| Agent | SWE-bench, AgentBench | Success rate |

## Resources

- EleutherAI LM Evaluation Harness: https://github.com/EleutherAI/lm-evaluation-harness
- SWE-bench: https://github.com/SWE-bench/SWE-bench
- AgentBench: https://github.com/THUDM/AgentBench
