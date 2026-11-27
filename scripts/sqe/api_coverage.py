#!/usr/bin/env python3
"""Measure API coverage of the team suite against the OpenAPI contract (EC-05, Lecture 20).

    .venv/bin/python scripts/sqe/api_coverage.py --evidence-dir NEW_DIR [--report FILE.md]

Runs the guarded team suite (tests.team, in-memory profile) and records every real
API call of its test client: test id, operation, status, media types, and the NAMES
of the fields sent and received. Values are kept only for enum fields, plus what the
operation-flow conditions need: the acting user's id, request ids, owners and dates
(synthetic fixture data). Credentials, tokens and other response values are never
stored. Coverage is computed from these calls, never from what a test claims to cover.

Output: coverage.json (covered/total/missing and test ids per criterion),
observed_cases.json (the generated-case manifest joined with observed status and
outcome), result.json, and optionally a Markdown report.
"""

import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stderr, redirect_stdout
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_tests  # noqa: E402 - the guarded runner and its environment report

ROOT = run_tests.ROOT
GENERATED = ROOT / "tests/team/generated"
# Cumulative levels of Lecture 20 as listed in TEST-STRATEGY; see the report's note.
LEVELS = [
    (1, ["paths"]), (2, ["operations"]), (3, ["request media types", "response media types"]),
    (4, ["parameters", "status-code classes"]), (5, ["parameter values", "status codes"]),
    (6, ["response body properties"]), (7, ["operation flows"]),
]


def response_paths(value, prefix=""):
    """Property paths of a JSON value; list positions collapse to []."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield f"{prefix}.{key}"
            yield from response_paths(item, f"{prefix}.{key}")
    elif isinstance(value, list):
        for item in value:
            yield from response_paths(item, prefix + "[]")


def documented_paths(schema, prefix=""):
    for part in schema.get("allOf", []) + schema.get("oneOf", []):
        yield from documented_paths(part, prefix)
    for key, item in schema.get("properties", {}).items():
        yield f"{prefix}.{key}"
        yield from documented_paths(item, f"{prefix}.{key}")
    if isinstance(schema.get("additionalProperties"), dict):
        yield f"{prefix}.*"
    if "items" in schema:
        yield from documented_paths(schema["items"], prefix + "[]")


class Trace:
    """Records real test-client calls per running test."""

    def __init__(self, contract):
        self.calls, self.test = [], None
        self.routes = [(name, op["method"], re.compile("^" + re.sub(r"{\w+}", "([^/]+)", op["path"]) + "$"))
                       for name, op in contract["operations"].items()]
        self.enums = {name: op["request_fields"] for name, op in contract["operations"].items()}

    def install(self):
        from rest_framework.test import APIRequestFactory
        from tests.team.runner import RecordingResult

        trace, generic, start = self, APIRequestFactory.generic, RecordingResult.startTest

        def recorded_generic(client, method, path, data="", content_type="application/octet-stream", *args, **kwargs):
            response = generic(client, method, path, data, content_type, *args, **kwargs)
            if hasattr(response, "status_code"):  # the factory alone returns a request
                trace.record(method, path, data, content_type, response)
            return response

        def recorded_start(result, test):
            trace.test = test.id()
            start(result, test)
        APIRequestFactory.generic, RecordingResult.startTest = recorded_generic, recorded_start

    def record(self, method, path, data, content_type, response):
        path = path.split("?")[0]
        name = match = None
        for candidate, verb, route in self.routes:
            match = route.match(path)
            if match and verb == method.lower():
                name = candidate
                break
        sent = {}
        media = (content_type or "").split(";")[0]
        if name and data:
            text = data.decode(errors="replace") if isinstance(data, bytes) else str(data)
            try:
                body = json.loads(text) if media == "application/json" else {}
            except ValueError:
                body = {}
            sent = body if isinstance(body, dict) else {}
            if media == "multipart/form-data":
                sent = dict(re.findall(r'name="(\w+)"\r\n\r\n([^\r]*)', text))
            elif media == "application/x-www-form-urlencoded":
                from urllib.parse import parse_qsl
                sent = dict(parse_qsl(text))
        kind = response.get("Content-Type", "").split(";")[0]
        paths, value = [], None
        if kind == "application/json" and response.content:
            value = response.json()
            paths = sorted(set(response_paths(value)))
        self.calls.append({
            "test": self.test, "operation": name, "method": method.lower(), "status": response.status_code,
            "path_parameters": list(match.groups()) if name and match else [],
            "request_media": media if data else None, "response_media": kind,
            "fields": sorted(sent), "response_paths": paths,
            "enum_values": {f: sent[f] for f, options in self.enums.get(name, {}).items()
                            if options and isinstance(sent.get(f), str) and sent[f] in options},
            **flow_facts(name, response, value, list(match.groups()) if name and match else []),
        })


def leave_record(value):
    """id, owner and dates of a serialized leave request, or None."""
    if isinstance(value, dict) and "id" in value and isinstance(value.get("employee"), dict):
        return {"id": str(value["id"]), "owner": value["employee"].get("id"),
                "start_date": value.get("start_date"), "end_date": value.get("end_date")}
    return None


def flow_facts(operation, response, value, path_parameters):
    """What the operation-flow conditions need from one call.

    actor: id of the authenticated user (DRF sets it on the underlying request);
    for a successful login, the user the token was issued to. record: the leave
    request the call created or decided (a refused decision knows only the path id).
    listed: request ids in a list or dashboard response. leaves: (member, start, end)
    of each team member's next approved leave.
    """
    user = getattr(getattr(response, "wsgi_request", None), "user", None)
    actor = user.pk if getattr(user, "is_authenticated", False) else None
    if operation == "login" and isinstance(value, dict) and isinstance(value.get("user"), dict):
        actor = value["user"].get("id")
    record = leave_record(value)
    if record is None and operation == "decideRequest" and path_parameters:
        record = {"id": path_parameters[0], "owner": None, "start_date": None, "end_date": None}
    items = value if isinstance(value, list) else value.get("recent", []) if isinstance(value, dict) else []
    listed = [r["id"] for r in map(leave_record, items) if r]
    leaves = [[m.get("id"), m["next_leave"]["start_date"], m["next_leave"]["end_date"]]
              for m in (value if operation == "team" and isinstance(value, list) else [])
              if isinstance(m, dict) and isinstance(m.get("next_leave"), dict)]
    return {"actor": actor, "record": record, "listed": listed, "leaves": leaves}


def flow_tests(flow, calls_by_test):
    """Tests whose calls contain the flow in order and meet every step condition."""
    return [test for test, calls in calls_by_test.items() if match_flow(flow["steps"], calls)]


STEP_KEYS = {"operation", "status", "decision", "same_record", "same_dates", "actor", "shows_record", "shows_leave"}


def owner(call):
    return (call.get("record") or {}).get("owner")


def step_matches(step, call, matched):
    """True when ``call`` is ``step``: operation, exact status and every condition on earlier steps."""
    unknown = set(step) - STEP_KEYS
    if unknown:
        raise ValueError(f"unknown x-operation-flows condition(s) {sorted(unknown)}")
    if call["operation"] != step["operation"] or call["status"] != step["status"]:
        return False
    record = call.get("record") or {}
    if "decision" in step and call["enum_values"].get("status") != step["decision"]:
        return False
    if "same_record" in step and (not record or record["id"] != (matched[step["same_record"]].get("record") or {}).get("id")):
        return False
    if "same_dates" in step:
        earlier = matched[step["same_dates"]].get("record") or {}
        if not record.get("start_date") or (record["start_date"], record["end_date"]) != (earlier.get("start_date"), earlier.get("end_date")):
            return False
    for relation, index in step.get("actor", {}).items():
        if relation not in ("same_as", "owner_of", "not_owner_of"):
            raise ValueError(f"unknown actor relation {relation!r}")
        expected = matched[index].get("actor") if relation == "same_as" else owner(matched[index])
        if call.get("actor") is None or expected is None:
            return False
        if (call["actor"] == expected) != (relation != "not_owner_of"):
            return False
    if "shows_record" in step and (matched[step["shows_record"]].get("record") or {}).get("id") not in call.get("listed", []):
        return False
    if "shows_leave" in step:
        earlier = matched[step["shows_leave"]].get("record") or {}
        if [owner(matched[step["shows_leave"]]), earlier.get("start_date"), earlier.get("end_date")] not in call.get("leaves", []):
            return False
    return True


def match_flow(steps, calls, matched=()):
    """Match the steps in order (other calls may come between); conditions refer to earlier matched steps."""
    if not steps:
        return True
    return any(step_matches(steps[0], call, list(matched)) and match_flow(steps[1:], calls[n + 1:], (*matched, call))
               for n, call in enumerate(calls))


def measure(contract, calls):
    operations = contract["operations"]
    known = [c for c in calls if c["operation"]]
    by_test = defaultdict(list)
    for call in known:
        by_test[call["test"]].append(call)
    hits = defaultdict(lambda: defaultdict(set))  # criterion -> item -> tests
    total = defaultdict(set)
    for name, op in operations.items():
        total["paths"].add(op["path"])
        total["operations"].add(name)
        total["parameters"] |= {f"{name}.{f}" for f in op["request_fields"]} | {f"{name}.path.{p}" for p in op["parameters"]}
        total["parameter values"] |= {f"{name}.{f}={v}" for f, options in op["request_fields"].items() for v in options or []}
        total["request media types"] |= {f"{name} {m}" for m in op["request_media"]}
        for code, content in op["responses"].items():
            total["status codes"].add(f"{name} {code}")
            total["status-code classes"].add(f"{name} {code[0]}xx")
            for media, schema in content.items():
                total["response media types"].add(f"{name} {media}")
                total["response body properties"] |= {f"{name} {code} {p}" for p in documented_paths(schema)}
    for call in known:
        name, op, test = call["operation"], operations[call["operation"]], call["test"]
        add = lambda criterion, item: hits[criterion][item].add(test)  # noqa: E731
        add("paths", op["path"])
        add("operations", name)
        for field in call["fields"]:
            add("parameters", f"{name}.{field}")
        for parameter in op["parameters"]:
            add("parameters", f"{name}.path.{parameter}")
        success = 200 <= call["status"] < 300
        if success:  # a value or media type counts when the operation accepted it
            for field, value in call["enum_values"].items():
                add("parameter values", f"{name}.{field}={value}")
            if call["request_media"]:
                add("request media types", f"{name} {call['request_media']}")
        add("status codes", f"{name} {call['status']}")
        add("status-code classes", f"{name} {str(call['status'])[0]}xx")
        add("response media types", f"{name} {call['response_media']}")
        prefix = f"{name} {call['status']} "
        for path in call["response_paths"]:
            item = prefix + path
            add("response body properties", item)
            if item not in total["response body properties"]:
                add("response body properties", prefix + path.rsplit(".", 1)[0] + ".*")
    for flow in contract["flows"]:
        total["operation flows"].add(flow["name"])
        for test in flow_tests(flow, by_test):
            hits["operation flows"][flow["name"]].add(test)
    result = {}
    for criterion, items in total.items():
        covered = {i for i in items if hits[criterion].get(i)}
        result[criterion] = {
            "covered": len(covered), "total": len(items), "missing": sorted(items - covered),
            "items": {i: {"test_count": len(hits[criterion][i]), "tests": sorted(hits[criterion][i])[:3]} for i in sorted(covered)},
            "undocumented_observed": sorted(set(hits[criterion]) - items) if criterion == "status codes" else [],
        }
    level = 0
    for number, criteria in LEVELS:
        if any(result[c]["missing"] for c in criteria):
            break
        level = number
    return result, level


def techniques(report, manifest):
    """Executed test methods per technique; each method is counted under one heading only."""
    count = Counter()
    for case in report["cases"]:
        module, _, method = case["id"].partition("tests.team.")[2].partition(".test_")
        headings = [
            ("generated.test_generated_api.", "generated EP/BVA (manifest)"),
            ("structural.test_ep_bva.BoundaryValue", "BVA, handwritten"), ("structural.test_ep_bva.", "EP, handwritten"),
            ("structural.test_decision_table", "decision tables"), ("structural.test_state_transition", "state transitions"),
            ("integration.", "cross-workflow integration"), ("api.test_openapi_contract", "contract"),
            ("api.", "A2.1 API functional"), ("foundation.", "foundation"), ("generated.", "manifest checks"),
        ]
        name = case["id"].removeprefix("tests.team.")
        count[next((label for start, label in headings if name.startswith(start)), "other")] += 1
    classes = Counter(
        f"{c['technique']} {'valid' if c['valid'] else 'invalid'}" for case in manifest["cases"] for c in case["classes"])
    return dict(count), dict(classes)


def markdown(data):
    lines = [
        "# API coverage (measured)", "",
        f"Generated by `scripts/sqe/api_coverage.py` from executed calls; do not edit. Commit `{data['git_sha'][:7]}`, "
        f"{data['counts']['executed']} team tests run, {data['counts']['passed']} passed. Spec SHA-256 `{data['spec_sha256'][:16]}…`.", "",
        "## REST criteria (Lecture 20)", "",
        "| Criterion | Covered | Total | % | Missing | Example tests |", "|---|---|---|---|---|---|",
    ]
    for criterion in [c for _, group in LEVELS for c in group]:
        row = data["criteria"][criterion]
        percent = 100 * row["covered"] / row["total"]
        example = next(iter(row["items"].values()), {"tests": []})["tests"][:1]
        lines.append(f"| {criterion} | {row['covered']} | {row['total']} | {percent:.1f} | "
                     f"{', '.join(row['missing']) or '—'} | {', '.join('`' + t.removeprefix('tests.team.') + '`' for t in example)} |")
    lines += [
        "", f"**Achieved level: TCL{data['achieved_level']}.** Target: **PENDING — team decision (EC-05)**; proposed target TCL7.", "",
        "Level mapping used: " + "; ".join(f"TCL{n} = {' + '.join(c)}" for n, c in LEVELS)
        + ". Cumulative. The mapping was compared with the Lecture 20 text and Martin-Lopez, Segura and Ruiz-Cortés "
        "(A-TEST 2019); the team still decides the target.", "",
        "Every covered item and its test ids are in `coverage.json` of the evidence directory.", "",
        "**Counting rules.** A path, operation or parameter counts when sent in a real call; an enum value or request media type "
        "only when the operation accepted it (2xx); status codes, media types and properties when observed in a response. "
        "Operation flows are the sequences in the spec's `x-operation-flows`. A flow counts only when every step returns its "
        "documented status and meets its conditions: the decision value sent, the same request id or dates, the acting user "
        "(same user, record owner, or not the owner) and the record shown in a later read.", "",
        "**Exclusions.** HEAD, OPTIONS, the HTML browsable API and 406 (framework features outside the selected scope); 405, which "
        "OpenAPI cannot document for a method that does not exist (generated and asserted, not counted); the Authorization header, "
        "which is a security scheme and not a parameter in OpenAPI (generated EP cases exist); the `/health/` probe (not a selected endpoint).", "",
        "**Undocumented responses observed** (deviations, see `docs/sqe/defects/`): "
        + (", ".join(f"`{i}`" for i in data["criteria"]["status codes"]["undocumented_observed"]) or "none") + ".", "",
        "## Techniques", "", "Each executed test method is counted once.", "", "| Suite | Executed tests |", "|---|---|",
    ]
    lines += [f"| {k} | {v} |" for k, v in sorted(data["techniques"].items())]
    lines += ["", "Classes and boundary points covered by the generated tests (one test can cover several): "
              + ", ".join(f"{k} {v}" for k, v in sorted(data["generated_classes"].items())) + ".", "",
              f"Generated cases: {data['observed']['matching']} of {data['observed']['total']} observed the expected status and passed. "
              "Techniques that do not apply, with reasons, are in `not_applicable` of `tests/team/generated/generated_cases.json`.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--evidence-dir", type=Path, required=True, help="NEW directory for the JSON evidence")
    parser.add_argument("--report", type=Path, help="Markdown report to write")
    args = parser.parse_args()
    directory = args.evidence_dir.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    contract = json.loads((GENERATED / "api_contract.json").read_text(encoding="utf-8"))
    manifest = json.loads((GENERATED / "generated_cases.json").read_text(encoding="utf-8"))
    before = run_tests.development_fingerprint()
    report = {"environment": run_tests.environment(), "started_at_utc": run_tests.utc_now()}

    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.team.settings"
    import django
    django.setup()
    trace = Trace(contract)
    trace.install()
    with (directory / "run.log").open("x") as log, redirect_stdout(log), redirect_stderr(log):
        exit_code = run_tests.run_django("team", ["tests.team"], 1, report)
    unchanged = before == run_tests.development_fingerprint()
    criteria, level = measure(contract, trace.calls)
    outcome = {c["id"]: c["outcome"] for c in report["cases"]}
    last = {call["test"]: call["status"] for call in trace.calls}
    observed = [{"id": c["id"], "expected_status": c["expected"]["status"], "observed_status": last.get(c["id"]),
                 "outcome": outcome.get(c["id"], "not run")} for c in manifest["cases"]]
    suites, classes = techniques(report, manifest)
    data = {
        "git_sha": report["environment"]["git_sha"], "git_status": report["environment"]["git_status"],
        "spec_sha256": contract["spec_sha256"], "counts": report["counts"], "recorded_calls": len(trace.calls),
        "criteria": criteria, "achieved_level": level, "techniques": suites, "generated_classes": classes,
        "observed": {"total": len(observed), "matching": sum(
            o["expected_status"] == o["observed_status"] and o["outcome"] == "passed" for o in observed)},
    }
    report.update(process_exit_code=exit_code, development_database_unchanged=unchanged, finished_at_utc=run_tests.utc_now())
    for name, value in (("coverage.json", data), ("observed_cases.json", observed), ("result.json", report)):
        (directory / name).write_text(json.dumps(value, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.report:
        args.report.write_text(markdown(data), encoding="utf-8")
    for criterion, row in criteria.items():
        print(f"{criterion}: {row['covered']}/{row['total']}" + (f"  missing {row['missing']}" if row["missing"] else ""))
    print(f"Achieved level TCL{level}; generated cases as expected {data['observed']['matching']}/{data['observed']['total']}; "
          f"tests {report['counts']}; development database unchanged={unchanged}")
    return exit_code or int(not unchanged)


if __name__ == "__main__":
    raise SystemExit(main())
