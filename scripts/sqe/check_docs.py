#!/usr/bin/env python3
"""Documentation consistency checks for the SQE project (read-only).

Usage (repository root):  python3 scripts/sqe/check_docs.py

1. Every relative Markdown link under docs/sqe (excluding generated evidence
   reports) points to an existing file, and every #anchor to an existing heading
   (GitHub-style slugs).
2. Use-case flow IDs agree across tests/team/browser/flows.json, the RTM
   "Browser use-case flow catalog (v0.2)" table and USE-CASE-SPECIFICATIONS.md:
   same ID set, no duplicates, owners and legacy IDs consistent, every v0.1
   E2E-UC row in the RTM carries a v0.1 disposition.

Exit code 0 when everything is consistent, 1 otherwise. Nothing is written.
"""

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "sqe"
RTM = DOCS / "planning" / "REQUIREMENTS-TRACEABILITY-MATRIX.md"
SPEC = DOCS / "requirements" / "USE-CASE-SPECIFICATIONS.md"
REGISTRY = ROOT / "tests" / "team" / "browser" / "flows.json"
problems = []


def slug(heading):
    text = re.sub(r"[`*_]", "", re.sub(r"<[^>]+>", "", heading)).strip().lower()
    return "".join(ch for ch in text if ch.isalnum() or ch in "-_ ").replace(" ", "-")


def anchors(md):
    seen, result, fenced = {}, set(), False
    for line in md.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            fenced = not fenced
        match = None if fenced else re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            base = slug(match.group(2))
            count = seen.get(base, 0)
            result.add(base if count == 0 else f"{base}-{count}")
            seen[base] = count + 1
    return result


def check_links():
    checked = 0
    for md in sorted(DOCS.rglob("*.md")):
        if "evidence" in md.relative_to(DOCS).parts:
            continue  # generated run reports are evidence, not maintained docs
        text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
                continue
            checked += 1
            path, _, fragment = target.partition("#")
            dest = md if not path else (md.parent / path).resolve()
            if not dest.exists():
                problems.append(f"broken link: {md.relative_to(ROOT)} -> {target}")
            elif fragment and dest.suffix == ".md" and fragment not in anchors(dest):
                problems.append(f"missing anchor: {md.relative_to(ROOT)} -> {target}")
    return checked


def check_ids():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    mandatory = registry["mandatory_flows"]
    others = registry["blocked_regression_objectives"] + registry["supplementary_checks"] + registry.get("included_use_cases", [])
    reg_ids = [f["id"] for f in mandatory + others]
    if len(mandatory) != 30:
        problems.append(f"flows.json: expected 30 mandatory flows, found {len(mandatory)}")
    for dup in {i for i in reg_ids if reg_ids.count(i) > 1}:
        problems.append(f"flows.json: duplicate id {dup}")

    rtm = RTM.read_text(encoding="utf-8")
    section = rtm.split("## Browser use-case flow catalog (v0.2)", 1)
    if len(section) != 2:
        problems.append("RTM: catalog section missing")
        return 0
    rows = [l for l in section[1].split("\n## ", 1)[0].splitlines() if re.match(r"^\| (TC|INC|OBJ|SUP)-", l)]
    rtm_ids = [r.split("|")[1].strip() for r in rows]
    for dup in {i for i in rtm_ids if rtm_ids.count(i) > 1}:
        problems.append(f"RTM catalog: duplicate id {dup}")
    for missing in sorted(set(reg_ids) - set(rtm_ids)):
        problems.append(f"RTM catalog: missing {missing}")
    for extra in sorted(set(rtm_ids) - set(reg_ids)):
        problems.append(f"RTM catalog: not in flows.json {extra}")
    legacy_rtm = {r.split("|")[1].strip(): r.split("|")[7].strip() for r in rows}
    for flow in mandatory:
        expected = ", ".join(flow.get("legacy_ids", [])) or "—"
        if legacy_rtm.get(flow["id"]) not in (expected, None):
            problems.append(f"legacy id mismatch for {flow['id']}: RTM {legacy_rtm.get(flow['id'])} vs flows.json {expected}")
        owner_num = flow.get("owner", "").replace("Member ", "M")
        row = next((r for r in rows if r.split("|")[1].strip() == flow["id"]), "")
        if owner_num and f"({owner_num})" not in row:
            problems.append(f"owner mismatch for {flow['id']}: flows.json {flow.get('owner')}")

    for line in rtm.splitlines():
        if re.match(r"^\| E2E-UC0\d-0\d \|", line) and "**v0.1 —" not in line:
            problems.append(f"RTM: v0.1 row without disposition: {line[:40]}")

    spec = SPEC.read_text(encoding="utf-8")
    for flow in mandatory:
        if flow["id"] not in spec:
            problems.append(f"spec: {flow['id']} not specified")
    return len(rtm_ids)


links = check_links()
ids = check_ids()
print(f"links checked: {links}; catalog ids checked: {ids}; problems: {len(problems)}")
for problem in problems:
    print(" -", problem)
sys.exit(1 if problems else 0)
