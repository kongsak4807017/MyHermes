#!/usr/bin/env python3
"""
ARIS Review Router for Hermes

Routes content to appropriate review type and prepares review prompt.
"""
import argparse, pathlib, json, sys

REVIEW_TYPES = {
    "paper-claim": "Verify every claim has evidence. Check for unsupported assertions, circular reasoning, and unstated assumptions.",
    "citation": "Verify citations exist and support claims. Check for hallucinated references, misattributed quotes, and outdated sources.",
    "proof": "Verify mathematical proofs are correct. Check for logical gaps, unstated lemmas, and incorrect applications.",
    "security": "Identify security vulnerabilities. Check for injection risks, auth flaws, data exposure, and misconfigurations.",
    "architecture": "Review system architecture decisions. Check for scalability, reliability, and maintainability issues.",
    "compliance": "Check regulatory compliance. Verify HIPAA, GDPR, Thai FDA, or other relevant frameworks.",
    "kill-argument": "Adversarial review: construct strongest rejection memo, then adjudicate point-by-point.",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("content_file", type=pathlib.Path)
    parser.add_argument("--review-type", required=True, choices=list(REVIEW_TYPES.keys()))
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args()

    if not args.content_file.exists():
        print(f"ERROR: File not found: {args.content_file}")
        sys.exit(1)

    content = args.content_file.read_text()
    
    review_package = {
        "review_type": args.review_type,
        "criteria": REVIEW_TYPES[args.review_type],
        "content_length": len(content),
        "content_preview": content[:500] + "..." if len(content) > 500 else content,
        "full_content": content,
        "output_format": {
            "verdicts": [
                {
                    "target": "string — what was reviewed",
                    "verdict": "PASS | FAIL | FIX | KEEP | REPLACE | REMOVE | USER_DECISION",
                    "evidence": "string — file:line or quote supporting verdict",
                    "suggestion": "string — optional fix proposal"
                }
            ]
        }
    }

    output = json.dumps(review_package, indent=2, ensure_ascii=False)
    
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Review package written: {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()
