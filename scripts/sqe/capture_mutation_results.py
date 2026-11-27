"""Archive actual metadata and normalized mutant diffs without executing mutants."""

import argparse
import ast
import copy
from collections import Counter
import difflib
import json
import os
import hashlib
from pathlib import Path
import subprocess


def mutant_diff(source, name):
    tree = ast.parse(source.read_text(encoding="utf-8"))
    functions = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    mutant = name.rsplit(".", 1)[1]
    original = mutant.rsplit("__mutmut_", 1)[0] + "__mutmut_orig"
    before, after = copy.deepcopy(functions[original]), copy.deepcopy(functions[mutant])
    before.name = after.name = "reviewed_function"
    before.decorator_list = after.decorator_list = []
    return "\n".join(difflib.unified_diff(ast.unparse(before).splitlines(), ast.unparse(after).splitlines(), fromfile="original", tofile="mutant", lineterm=""))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    args.output = args.output.resolve()
    os.chdir(args.root.resolve())
    args.output.mkdir(parents=True, exist_ok=False)
    rows = []
    for path in sorted(Path("mutants").rglob("*.meta")):
        metadata = json.loads(path.read_text(encoding="utf-8"))
        source = path.with_suffix("")
        tree = ast.parse(source.read_text(encoding="utf-8"))
        functions = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        for name, code in metadata["exit_code_by_key"].items():
            mutant = name.rsplit(".", 1)[1]
            original = mutant.rsplit("__mutmut_", 1)[0] + "__mutmut_orig"
            before, after = copy.deepcopy(functions[original]), copy.deepcopy(functions[mutant])
            before.name = after.name = "reviewed_function"
            before.decorator_list = after.decorator_list = []
            diff = "\n".join(difflib.unified_diff(ast.unparse(before).splitlines(), ast.unparse(after).splitlines(), lineterm=""))
            rows.append({"id": name, "source": str(source.relative_to("mutants")).replace("\\", "/"),
                         "exit_code": code, "result": "survived" if code == 0 else "killed" if code in (1, 3) else "unresolved",
                         "diff": diff})
    counts = Counter(row["result"] for row in rows)
    stats = {"killed": counts["killed"], "survived": counts["survived"], "total": len(rows),
             "unresolved": counts["unresolved"]}
    Path("mutants/mutmut-cicd-stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    evidence = {"git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                "source_sha256": {str(path).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in Path("backend").rglob("*.py")},
                "counts": stats, "mutants": rows}
    (args.output / "results.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
