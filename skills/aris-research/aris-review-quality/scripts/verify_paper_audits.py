#!/usr/bin/env python3
"""
HERMES PORT of ARIS verify_paper_audits.sh

Validates that all mandatory audits have emitted verdicts.
Returns 0 if all green, 1 if any FAIL/USER_DECISION unresolved.

Usage:
    python3 verify_paper_audits.py <paper_dir> [--assurance submission|draft]
"""
import sys, json, pathlib, argparse, os

VERDICT_ORDER = ["PASS", "KEEP", "FIX", "REPLACE", "REMOVE", "FAIL", "USER_DECISION"]
MANDATORY_AUDITS = ["proof-checker", "paper-claim-audit", "citation-audit", "kill-argument"]

def load_audit(paper_dir: pathlib.Path, audit_name: str) -> dict:
    audit_file = paper_dir / f"AUDIT_{audit_name}.json"
    if not audit_file.exists():
        return {"status": "MISSING", "verdicts": []}
    try:
        return json.loads(audit_file.read_text())
    except json.JSONDecodeError:
        return {"status": "CORRUPT", "verdicts": []}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paper_dir", type=pathlib.Path)
    parser.add_argument("--assurance", default="draft", choices=["draft", "submission"])
    args = parser.parse_args()

    if not args.paper_dir.exists():
        print(f"ERROR: Directory not found: {args.paper_dir}")
        sys.exit(1)

    all_ok = True
    results = []

    for audit in MANDATORY_AUDITS:
        data = load_audit(args.paper_dir, audit)
        verdicts = data.get("verdicts", [])
        
        if data["status"] == "MISSING":
            if args.assurance == "submission":
                print(f"[FAIL] {audit}: MISSING (required in submission mode)")
                all_ok = False
            else:
                print(f"[SKIP] {audit}: MISSING (draft mode allows silent skip)")
            continue

        # Check for FAIL or USER_DECISION
        critical = [v for v in verdicts if v.get("verdict") in ("FAIL", "USER_DECISION")]
        if critical:
            print(f"[FAIL] {audit}: {len(critical)} critical verdicts")
            all_ok = False
        else:
            print(f"[PASS] {audit}: {len(verdicts)} verdicts, all acceptable")

        results.append({"audit": audit, "verdicts": verdicts})

    # Write master report
    report = args.paper_dir / "AUDIT_MASTER.json"
    report.write_text(json.dumps({
        "assurance": args.assurance,
        "all_ok": all_ok,
        "results": results,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }, indent=2, ensure_ascii=False))

    print(f"\nReport written: {report}")
    print(f"Overall: {'PASS' if all_ok else 'FAIL'}")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
