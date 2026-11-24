"""Create a review table from completed mutmut results.

The generated table is intentionally a draft: the rule impact and killability
judgement must be reviewed by a student against the actual diff before it is
submitted as evidence.
"""

from pathlib import Path

from mutmut.mutation.data import SourceFileMutationData
from mutmut.stats import status_by_exit_code


def main() -> int:
    rows = []
    for metadata in sorted(Path("mutants").rglob("*.meta")):
        source = Path(str(metadata)[: -len(".meta")])
        data = SourceFileMutationData(path=source)
        data.load()
        for name, exit_code in data.exit_code_by_key.items():
            if status_by_exit_code[exit_code] == "survived":
                rows.append((name, source.as_posix()))

    output = Path("docs/sqe/evidence/area1/mutation/surviving-mutants.md")
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Surviving-mutant analysis",
        "",
        "Generated from the mutmut result for the current commit. Replace the "
        "draft cells with source-grounded analysis before submission.",
        "",
        "| # | Mutant | Source | Affected rule | Killable? | Test or equivalence justification |",
        "|---:|---|---|---|---|---|",
    ]
    for index, (name, source) in enumerate(rows, start=1):
        lines.append(f"| {index} | `{name}` | `{source}` | TBD | TBD | TBD |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} surviving mutants to {output}")
    return 0 if len(rows) >= 15 else 1


if __name__ == "__main__":
    raise SystemExit(main())
