#!/usr/bin/env python3
"""
SWE-bench evaluation runner for AI coding agents.
"""

import json
import subprocess
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class SWEBenchPrediction:
    """Single SWE-bench prediction."""
    instance_id: str
    model_patch: str
    model_name_or_path: str = "agent"


@dataclass
class SWEBenchResult:
    """Result for a single instance."""
    instance_id: str
    resolved: bool
    test_results: Dict
    error: Optional[str] = None


class SWEBenchRunner:
    """Run SWE-bench evaluation."""

    def __init__(self, dataset: str = "princeton-nlp/SWE-bench_Lite",
                 max_workers: int = 4):
        self.dataset = dataset
        self.max_workers = max_workers

    def prepare_predictions(self, predictions: List[SWEBenchPrediction],
                           output_path: str = "predictions.json"):
        """Save predictions in SWE-bench format."""
        data = [asdict(p) for p in predictions]
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Predictions saved to {output_path}")

    def run_evaluation(self, predictions_path: str,
                      run_id: str = "test_run") -> Dict:
        """Run SWE-bench evaluation."""
        cmd = [
            "python", "-m", "swebench.harness.run_evaluation",
            "--dataset_name", self.dataset,
            "--predictions_path", predictions_path,
            "--max_workers", str(self.max_workers),
            "--run_id", run_id,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return {"error": result.stderr}

        # Load results
        results_path = f"results/{run_id}.json"
        if os.path.exists(results_path):
            with open(results_path) as f:
                return json.load(f)

        return {"stdout": result.stdout}

    def analyze_results(self, results: Dict) -> Dict:
        """Analyze evaluation results."""
        total = len(results.get("results", []))
        resolved = sum(1 for r in results.get("results", [])
                      if r.get("resolved", False))

        return {
            "total": total,
            "resolved": resolved,
            "accuracy": resolved / total if total > 0 else 0,
            "by_repo": self._group_by_repo(results.get("results", [])),
        }

    def _group_by_repo(self, results: List[Dict]) -> Dict:
        """Group results by repository."""
        repos = {}
        for r in results:
            repo = r["instance_id"].split("__")[0]
            if repo not in repos:
                repos[repo] = {"total": 0, "resolved": 0}
            repos[repo]["total"] += 1
            if r.get("resolved", False):
                repos[repo]["resolved"] += 1

        # Calculate accuracy per repo
        for repo in repos:
            repos[repo]["accuracy"] = (
                repos[repo]["resolved"] / repos[repo]["total"]
            )

        return repos


class SWEBenchMockRunner:
    """Mock runner for testing without SWE-bench installed."""

    def __init__(self):
        self.predictions: List[SWEBenchPrediction] = []

    def prepare_predictions(self, predictions: List[SWEBenchPrediction],
                           output_path: str = "predictions.json"):
        """Save predictions."""
        self.predictions = predictions
        data = [asdict(p) for p in predictions]
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    def mock_evaluate(self) -> Dict:
        """Run mock evaluation."""
        results = []
        for pred in self.predictions:
            # Mock result (50% success rate)
            import hashlib
            h = hashlib.md5(pred.instance_id.encode()).hexdigest()
            resolved = int(h, 16) % 2 == 0

            results.append({
                "instance_id": pred.instance_id,
                "resolved": resolved,
                "test_results": {"passed": resolved, "total": 1},
            })

        return {
            "results": results,
            "total": len(results),
            "resolved": sum(1 for r in results if r["resolved"]),
        }


if __name__ == "__main__":
    # Demo with mock runner
    runner = SWEBenchMockRunner()

    predictions = [
        SWEBenchPrediction(
            instance_id="django__django-1234",
            model_patch="diff --git a/django/...",
        ),
        SWEBenchPrediction(
            instance_id="scikit-learn__scikit-learn-5678",
            model_patch="diff --git a/sklearn/...",
        ),
    ]

    runner.prepare_predictions(predictions)
    results = runner.mock_evaluate()

    print("SWE-bench Mock Results:")
    print(json.dumps(results, indent=2))
