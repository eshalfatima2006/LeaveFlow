"""Fail CI when mutmut's killed-mutant score is below the project threshold."""

import json
import sys
from pathlib import Path

# Require at least 85% killed/total while rejecting all incomplete result
# categories below. The threshold is a justified minimum; the current hosted
# PR #17 result is 99.00% (296/299, run 76).
THRESHOLD = 0.85
RESULTS = Path("mutants/mutmut-cicd-stats.json")


def main() -> int:
    results = Path(sys.argv[1]) if len(sys.argv) > 1 else RESULTS
    if not results.exists():
        print(f"Mutation results are missing: {results}", file=sys.stderr)
        return 1
    data = json.loads(results.read_text(encoding="utf-8"))
    data = data.get("counts", data)
    if data.get("unresolved", 0):
        print("Mutation run includes unresolved mutants.", file=sys.stderr)
        return 1
    incomplete = {key: data.get(key, 0) for key in (
        "no_tests", "skipped", "suspicious", "timeout", "check_was_interrupted_by_user", "segfault"
    ) if data.get(key, 0)}
    if incomplete:
        print(f"Mutation run is incomplete or untested: {incomplete}", file=sys.stderr)
        return 1
    tested = data["killed"] + data["survived"]
    if data.get("total") != tested:
        print("Mutation total includes unclassified or unevaluated mutants.", file=sys.stderr)
        return 1
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
