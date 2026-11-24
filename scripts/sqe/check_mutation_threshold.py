"""Fail CI when mutmut's killed-mutant score is below the project threshold."""

import json
import sys
from pathlib import Path

# The score is calculated only from mutants with an associated test.  This
# baseline is intentionally explicit so future changes cannot reduce the
# current tested-mutant score without failing CI.
THRESHOLD = 0.60
RESULTS = Path("mutants/mutmut-cicd-stats.json")


def main() -> int:
    if not RESULTS.exists():
        print(f"Mutation results are missing: {RESULTS}", file=sys.stderr)
        return 1
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    tested = data["killed"] + data["survived"]
    if tested == 0:
        print("Mutation run produced no tested mutants.", file=sys.stderr)
        return 1
    score = data["killed"] / tested
    print(f"Mutation score: {score:.2%} ({data['killed']}/{tested}); threshold: {THRESHOLD:.0%}")
    if score < THRESHOLD:
        print("Mutation quality gate failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
