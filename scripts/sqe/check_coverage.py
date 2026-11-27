"""Enforce the assignment's 100% statement and branch coverage gate."""

import json
import sys
from pathlib import Path

TARGETS = (
    "backend/leave/models.py",
    "backend/leave/serializers.py",
    "backend/leave/views.py",
    "backend/leave/events.py",
)


def main() -> int:
    report = Path("coverage.json")
    if not report.exists():
        print("coverage.json is missing; run coverage json first.", file=sys.stderr)
        return 1
    data = json.loads(report.read_text(encoding="utf-8"))
    measured = {
        filename.replace("\\", "/"): details
        for filename, details in data["files"].items()
    }
    failures = []
    for filename in TARGETS:
        summary = measured.get(filename, {}).get("summary")
        if summary is None:
            failures.append(f"{filename}: not measured")
            continue
        statements = summary["covered_lines"] / max(summary["num_statements"], 1)
        branches = summary["covered_branches"] / max(summary["num_branches"], 1)
        print(f"{filename}: statements={statements:.2%}, branches={branches:.2%}")
        if summary["missing_lines"] or summary["num_branches"] != summary["covered_branches"]:
            failures.append(
                f"{filename}: missing lines={summary['missing_lines']}, "
                f"missing branches={summary['num_branches'] - summary['covered_branches']}"
            )
    if failures:
        print("Coverage quality gate failed:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
