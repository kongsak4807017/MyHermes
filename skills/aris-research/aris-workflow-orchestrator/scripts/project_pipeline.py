#!/usr/bin/env python3
"""
ARIS Project Pipeline for Hermes
Adapts research workflows to technical projects (Smart Hospital, IOC, etc.)
"""
import argparse, pathlib, json, os, sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("topic")
    parser.add_argument("--type", default="research", choices=["research", "smart-hospital", "ioc-system"])
    parser.add_argument("--effort", default="balanced")
    parser.add_argument("--assurance", default="draft")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--output-dir", type=pathlib.Path, default=pathlib.Path("."))
    args = parser.parse_args()

    # Create project structure
    project_dir = args.output_dir / f"aris-project-{args.type}"
    project_dir.mkdir(parents=True, exist_ok=True)

    phases = {
        "research": ["W1-Discovery", "W1.5-Experiments", "W2-Review", "W3-Writing", "W4-Rebuttal", "W5-Resubmit"],
        "smart-hospital": ["W1-Clinical-Discovery", "W1.5-Prototype", "W2-Compliance", "W3-Documentation", "W4-Regulatory", "W5-Deployment"],
        "ioc-system": ["W1-Operations-Discovery", "W1.5-Simulation", "W2-Security", "W3-Operations-Doc", "W4-Stakeholder", "W5-Multi-Agency"]
    }

    manifest = {
        "topic": args.topic,
        "type": args.type,
        "effort": args.effort,
        "assurance": args.assurance,
        "lang": args.lang,
        "phases": phases.get(args.type, phases["research"]),
        "project_dir": str(project_dir),
        "status": "INIT",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }

    manifest_file = project_dir / "PROJECT_MANIFEST.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print(f"Project initialized: {project_dir}")
    print(f"  Type: {args.type}")
    print(f"  Topic: {args.topic}")
    print(f"  Phases: {', '.join(manifest['phases'])}")
    print(f"  Manifest: {manifest_file}")

    # Create phase directories
    for phase in manifest["phases"]:
        (project_dir / phase).mkdir(exist_ok=True)
        (project_dir / phase / "README.md").write_text(f"# {phase}\n\nTopic: {args.topic}\n", encoding="utf-8")

    return 0

if __name__ == "__main__":
    sys.exit(main())
