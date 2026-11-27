"""Create a review table from completed mutmut results.

The metadata files live under ``mutants/``, but mutmut's
``SourceFileMutationData`` expects the original source path and adds the
``mutants/`` prefix itself.  Keeping those two paths separate is important:
passing the copied path makes every metadata record appear empty.
"""

from pathlib import Path
from capture_mutation_results import mutant_diff

from mutmut.mutation.data import SourceFileMutationData
from mutmut.stats import status_by_exit_code


def _source_path_from_metadata(metadata: Path) -> Path:
    """Return the original source path represented by a ``*.meta`` file."""

    copied_source = metadata.with_suffix("")
    try:
        return copied_source.relative_to("mutants")
    except ValueError as exc:
        raise ValueError(f"Unexpected mutmut metadata path: {metadata}") from exc


def _rule_for(source: Path) -> str:
    """Describe the area; classification requires an actual diff review."""

    rule_by_file = {
        "models.py": "Leave-request date/overlap and leave-balance invariant",
        "serializers.py": "Leave-request validation and balance enforcement",
        "views.py": "Request visibility, submission, or approval response flow",
        "events.py": "Leave-event publication behavior",
    }
    return rule_by_file.get(source.name, "Supporting leave-workflow behavior")


def main() -> int:
    survivors = []
    killed = []
    for metadata in sorted(Path("mutants").rglob("*.meta")):
        source = _source_path_from_metadata(metadata)
        data = SourceFileMutationData(path=source)
        data.load()
        for name, exit_code in data.exit_code_by_key.items():
            result = status_by_exit_code[exit_code]
            row = (name, source.as_posix(), result)
            if result == "survived":
                survivors.append(row)
            elif result == "killed":
                killed.append(row)

    rows = survivors

    output = Path("mutation-candidates.md")
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Mutation review candidates (not completed analysis)",
        "",
        "Generated from the actual mutmut metadata. Review each diff against the curated survivor analysis; tool output alone does not establish equivalence or killability.",
        "",
        "| # | Mutant | Source | Result | Affected rule | Killable? | Test or equivalence justification |",
        "|---:|---|---|---|---|---|---|",
    ]
    for index, (name, source, result) in enumerate(rows, start=1):
        rule = _rule_for(Path(source))
        killability, justification = "REVIEW REQUIRED", "Inspect the recorded diff and run a discriminating test."
        lines.append(
            f"| {index} | `{name}` | `{source}` | {result} | {rule} | "
            f"{killability} | {justification} |"
        )
    for name, source, result in survivors:
        diff = mutant_diff(Path("mutants") / source, name)
        lines += ["", f"## {name}", "", "```diff", diff.strip(), "```"]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} mutation review candidates to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
