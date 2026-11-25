#!/usr/bin/env python3
"""Collect package inventories and defensive advisory results without changing locks."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from browser_harness import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python-packages", type=Path, required=True, help="Isolated installed backend requirements")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    packages = args.python_packages.resolve(strict=True)
    output = args.evidence_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if npm is None:
        raise SystemExit("npm is required")
    status = {}

    def capture(name, command, cwd=ROOT):
        with (output / f"{name}.json").open("w", encoding="utf-8") as out:
            with (output / f"{name}.stderr").open("w", encoding="utf-8") as err:
                result = subprocess.run(command, cwd=cwd, stdout=out, stderr=err, check=False)
        status[name] = result.returncode

    capture("python", [sys.executable, "-m", "pip_audit", "--strict", "--path", str(packages), "--format", "json"])
    for name, directory in (
        ("frontend", ROOT / "frontend"), ("gateway", ROOT / "notifications"),
        ("browser", ROOT / "tests/team/browser"),
    ):
        capture(f"{name}-inventory", [npm, "ls", "--all", "--json"], directory)
        capture(f"{name}-advisories", [npm, "audit", "--json"], directory)
    (output / "exit-codes.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(json.dumps(status, indent=2))
    return int(any(status.values()))


if __name__ == "__main__":
    raise SystemExit(main())
