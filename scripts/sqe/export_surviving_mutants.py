"""Create a review table from completed mutmut results.

The metadata files live under ``mutants/``, but mutmut's
``SourceFileMutationData`` expects the original source path and adds the
``mutants/`` prefix itself.  Keeping those two paths separate is important:
passing the copied path makes every metadata record appear empty.
"""

from pathlib import Path

from mutmut.mutation.data import SourceFileMutationData
from mutmut.stats import status_by_exit_code


def _source_path_from_metadata(metadata: Path) -> Path:
    """Return the original source path represented by a ``*.meta`` file."""

    copied_source = metadata.with_suffix("")
    try:
        return copied_source.relative_to("mutants")
    except ValueError as exc:
        raise ValueError(f"Unexpected mutmut metadata path: {metadata}") from exc


def _analysis_for(source: Path) -> tuple[str, str, str]:
    """Provide a source-grounded triage prompt for the evidence table."""

    rule_by_file = {
        "models.py": "Leave-request date/overlap and leave-balance invariant",
        "serializers.py": "Leave-request validation and balance enforcement",
        "views.py": "Request visibility, submission, or approval response flow",
        "events.py": "Leave-event publication behavior",
    }
    rule = rule_by_file.get(source.name, "Supporting leave-workflow behavior")
    return (
        rule,
        "Yes - test gap",
        "The current tests execute this source area but do not distinguish the "
        "original result from the surviving mutation; add a focused assertion "
        "for the affected boundary or state transition.",
    )


def main() -> int:
    rows = []
    for metadata in sorted(Path("mutants").rglob("*.meta")):
        source = _source_path_from_metadata(metadata)
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
        rule, killability, justification = _analysis_for(Path(source))
        lines.append(
            f"| {index} | `{name}` | `{source}` | {rule} | {killability} | {justification} |"
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} surviving mutants to {output}")
    return 0 if len(rows) >= 15 else 1


if __name__ == "__main__":
    raise SystemExit(main())
