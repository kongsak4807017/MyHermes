#!/usr/bin/env python3
"""
Evaluation harness for AI agents.
Benchmark management, regression testing, and performance tracking.
"""

import json
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class BenchmarkResult:
    """Result from a single benchmark."""
    benchmark_name: str
    score: float
    metrics: Dict[str, float] = field(default_factory=dict)
    details: List[Dict] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class EvaluationReport:
    """Complete evaluation report."""
    model_name: str
    results: List[BenchmarkResult] = field(default_factory=list)
    total_duration: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def get_score(self, benchmark_name: str) -> Optional[float]:
        for r in self.results:
            if r.benchmark_name == benchmark_name:
                return r.score
        return None
    
    def get_average_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results) / len(self.results)
    
    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "timestamp": self.timestamp,
            "total_duration": self.total_duration,
            "average_score": self.get_average_score(),
            "results": [asdict(r) for r in self.results],
        }


class Benchmark:
    """Base class for benchmarks."""
    
    def __init__(self, name: str):
        self.name = name
    
    def run(self, model: Any) -> BenchmarkResult:
        """Run benchmark against model."""
        raise NotImplementedError


class MMLUBenchmark(Benchmark):
    """MMLU benchmark stub."""
    
    def __init__(self):
        super().__init__("mmlu")
    
    def run(self, model: Any) -> BenchmarkResult:
        start = time.time()
        # Mock implementation
        score = 0.65
        return BenchmarkResult(
            benchmark_name=self.name,
            score=score,
            metrics={"accuracy": score, "subjects": 57},
            duration_seconds=time.time() - start,
        )


class GSM8KBenchmark(Benchmark):
    """GSM8K benchmark stub."""
    
    def __init__(self):
        super().__init__("gsm8k")
    
    def run(self, model: Any) -> BenchmarkResult:
        start = time.time()
        score = 0.45
        return BenchmarkResult(
            benchmark_name=self.name,
            score=score,
            metrics={"exact_match": score, "problems": 1319},
            duration_seconds=time.time() - start,
        )


class HumanEvalBenchmark(Benchmark):
    """HumanEval benchmark stub."""
    
    def __init__(self):
        super().__init__("humaneval")
    
    def run(self, model: Any) -> BenchmarkResult:
        start = time.time()
        score = 0.55
        return BenchmarkResult(
            benchmark_name=self.name,
            score=score,
            metrics={"pass@1": score, "problems": 164},
            duration_seconds=time.time() - start,
        )


class EvaluationHarness:
    """Main evaluation harness."""
    
    def __init__(self):
        self.benchmarks: List[Benchmark] = []
        self.history: List[EvaluationReport] = []
    
    def add_benchmark(self, benchmark: Benchmark):
        """Add a benchmark."""
        self.benchmarks.append(benchmark)
    
    def run(self, model: Any, model_name: str = "unknown") -> EvaluationReport:
        """Run all benchmarks."""
        report = EvaluationReport(model_name=model_name)
        start = time.time()
        
        for benchmark in self.benchmarks:
            print(f"Running {benchmark.name}...")
            result = benchmark.run(model)
            report.results.append(result)
            print(f"  Score: {result.score:.3f}")
        
        report.total_duration = time.time() - start
        self.history.append(report)
        
        return report
    
    def save_report(self, report: EvaluationReport, path: str):
        """Save report to file."""
        with open(path, "w") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"Report saved to {path}")
    
    def load_report(self, path: str) -> EvaluationReport:
        """Load report from file."""
        with open(path) as f:
            data = json.load(f)
        
        report = EvaluationReport(
            model_name=data["model_name"],
            timestamp=data["timestamp"],
            total_duration=data["total_duration"],
        )
        
        for r in data["results"]:
            report.results.append(BenchmarkResult(
                benchmark_name=r["benchmark_name"],
                score=r["score"],
                metrics=r.get("metrics", {}),
                details=r.get("details", []),
                duration_seconds=r.get("duration_seconds", 0),
                timestamp=r.get("timestamp", time.time()),
            ))
        
        return report


class RegressionTester:
    """Test for regressions between versions."""
    
    def __init__(self, baseline: EvaluationReport = None):
        self.baseline = baseline
    
    def load_baseline(self, path: str):
        """Load baseline from file."""
        harness = EvaluationHarness()
        self.baseline = harness.load_report(path)
    
    def compare(self, new_report: EvaluationReport) -> Dict:
        """Compare new report with baseline."""
        if self.baseline is None:
            return {"error": "No baseline set"}
        
        improvements = []
        regressions = []
        unchanged = []
        
        for new_result in new_report.results:
            baseline_score = self.baseline.get_score(new_result.benchmark_name)
            
            if baseline_score is None:
                continue
            
            diff = new_result.score - baseline_score
            pct_change = (diff / baseline_score * 100) if baseline_score != 0 else 0
            
            comparison = {
                "benchmark": new_result.benchmark_name,
                "baseline": baseline_score,
                "new": new_result.score,
                "diff": diff,
                "pct_change": pct_change,
            }
            
            if diff > 0.01:
                improvements.append(comparison)
            elif diff < -0.01:
                regressions.append(comparison)
            else:
                unchanged.append(comparison)
        
        return {
            "has_regressions": len(regressions) > 0,
            "improvements": improvements,
            "regressions": regressions,
            "unchanged": unchanged,
            "overall_change": new_report.get_average_score() - self.baseline.get_average_score(),
        }


class PerformanceTracker:
    """Track performance over time."""
    
    def __init__(self):
        self.records: List[Dict] = []
    
    def record(self, version: str, report: EvaluationReport):
        """Record a version's performance."""
        self.records.append({
            "version": version,
            "timestamp": report.timestamp,
            "average_score": report.get_average_score(),
            "results": {r.benchmark_name: r.score for r in report.results},
        })
    
    def get_trend(self, benchmark_name: str) -> List[Dict]:
        """Get trend for a benchmark."""
        return [
            {
                "version": r["version"],
                "timestamp": r["timestamp"],
                "score": r["results"].get(benchmark_name),
            }
            for r in self.records
            if benchmark_name in r["results"]
        ]
    
    def to_dict(self) -> dict:
        return {
            "records": self.records,
            "benchmarks": list(self.records[0]["results"].keys()) if self.records else [],
        }
    
    def save(self, path: str):
        """Save tracking data."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


if __name__ == "__main__":
    # Demo: Run evaluation
    harness = EvaluationHarness()
    harness.add_benchmark(MMLUBenchmark())
    harness.add_benchmark(GSM8KBenchmark())
    harness.add_benchmark(HumanEvalBenchmark())
    
    report = harness.run(model=None, model_name="demo-model")
    
    print("\nEvaluation Report:")
    print(json.dumps(report.to_dict(), indent=2))
    
    # Demo: Regression testing
    harness.save_report(report, "/tmp/baseline.json")
    
    regression = RegressionTester()
    regression.load_baseline("/tmp/baseline.json")
    
    # Simulate new results
    new_report = EvaluationReport(model_name="demo-model-v2")
    new_report.results = [
        BenchmarkResult("mmlu", 0.70),
        BenchmarkResult("gsm8k", 0.40),  # Regression
        BenchmarkResult("humaneval", 0.60),
    ]
    
    comparison = regression.compare(new_report)
    print("\nRegression Report:")
    print(json.dumps(comparison, indent=2))
    
    # Demo: Performance tracking
    tracker = PerformanceTracker()
    tracker.record("v1.0", report)
    tracker.record("v1.1", new_report)
    
    print("\nPerformance Trend (MMLU):")
    print(json.dumps(tracker.get_trend("mmlu"), indent=2))
