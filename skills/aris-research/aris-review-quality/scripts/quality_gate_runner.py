#!/usr/bin/env python3
"""
ARIS Quality Gate Runner for Hermes

Runs all quality gates sequentially and produces a unified report.
Supports both research papers AND technical project deliverables.

Usage:
    python3 quality_gate_runner.py <project_dir> [--type paper|project] [--assurance submission|draft]
"""
import sys, json, pathlib, argparse, subprocess, os

GATES = {
    "paper": ["proof-checker", "paper-claim-audit", "citation-audit", "kill-argument"],
    "project": ["claim-audit", "citation-audit", "architecture-review", "security-audit"]
}

def run_gate(gate_name: str, project_dir: pathlib.Path, assurance: str) -> dict:
    """Run a single quality gate. In Hermes, this delegates to a subagent."""
    # For now, check if audit file exists and validate it
    audit_file = project_dir / f"AUDIT_{gate_name.replace('-', '_')}.json"
    if audit_file.exists():
        try:
            data = json.loads(audit_file.read_text())
            return {"gate": gate_name, "status": data.get("status", "UNKNOWN"), "verdicts": data.get("verdicts", [])}
        except:
            return {"gate": gate_name, "status": "CORRUPT", "verdicts": []}
    return {"gate": gate_name, "status": "MISSING", "verdicts": []}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=pathlib.Path)
    parser.add_argument("--type", default="paper", choices=["paper", "project"])
    parser.add_argument("--assurance", default="draft", choices=["draft", "submission"])
    args = parser.parse_args()

    gates = GATES.get(args.type, GATES["paper"])
    results = []
    all_ok = True

    print(f"Running {len(gates)} quality gates for {args.type} at assurance={args.assurance}")
    print("=" * 60)

    for gate in gates:
        result = run_gate(gate, args.project_dir, args.assurance)
        results.append(result)
        
        if result["status"] == "MISSING":
            if args.assurance == "submission":
                print(f"[BLOCK] {gate}: MISSING")
                all_ok = False
            else:
                print(f"[SKIP]  {gate}: MISSING (draft mode)")
        elif result["status"] == "CORRUPT":
            print(f"[BLOCK] {gate}: CORRUPT")
            all_ok = False
        else:
            critical = [v for v in result["verdicts"] if v.get("verdict") in ("FAIL", "USER_DECISION")]
            if critical:
                print(f"[BLOCK] {gate}: {len(critical)} critical")
                all_ok = False
            else:
                print(f"[PASS]  {gate}: OK")

    # Write report
    report = args.project_dir / "QUALITY_GATE_REPORT.json"
    report.write_text(json.dumps({
        "type": args.type,
        "assurance": args.assurance,
        "all_ok": all_ok,
        "gates": results,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }, indent=2, ensure_ascii=False))

    print(f"\nReport: {report}")
    print(f"Result: {'ALL GATES PASSED' if all_ok else 'SOME GATES BLOCKED'}")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
