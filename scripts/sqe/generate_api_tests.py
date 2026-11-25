#!/usr/bin/env python3
"""Generate EP/BVA API tests from the LeaveFlow OpenAPI specification (A2.4).

Usage:
    python3 scripts/sqe/generate_api_tests.py [SPEC] [--patch FILE] [--output PATH]
                                              [--demo-env NAME=VALUE]

SPEC defaults to docs/sqe/openapi/leaveflow-api.yaml and --output to
tests/team/generated/test_generated_api.py. Requires PyYAML
(scripts/sqe/requirements-generator.txt); the project .venv does not ship it, and
any Python 3 with PyYAML can run the generator, because it only reads YAML and
writes Python source. --patch applies a unified diff to a copy of SPEC in memory
(needs the `patch` command), so a constraint change never edits the baseline spec.

Inputs of every operation and the classes derived from the spec:

  body field    EP valid: each enum value / the declared type / null if nullable /
                omitted if optional. EP invalid: wrong type, out-of-enum, invalid
                format, null, missing, over-max-length, x-invalid-examples.
                x-trimmed-max-length adds whitespace-only, padded-at-limit (valid)
                and padded-over-limit (invalid).
                BVA: limit-1, limit, limit+1 for maxLength, x-trimmed-max-length,
                minLength, minimum, maximum and x-relational.
  rule limit    x-rule-boundaries: BVA of business days against the fixture
                allowance and of both ends of the fixture's existing interval.
  path          x-invalid-examples of the parameter (404).
  context       x-context-cases: actor and target record, one at a time.
  Authorization valid, missing and unknown token (401).
  media         every documented request media type (valid), malformed JSON (400),
                text/plain (415).
  method        each of GET/POST/PUT/PATCH/DELETE the path does not document (405).

Each case changes one input of the operation's example request (a rule limit sets
its start/end pair, one interval input). Cases that yield the same request are
merged into one test whose docstring lists every class; the same request with
contradictory expectations aborts generation. Techniques that do not apply, and
infeasible points, are listed with a reason in the manifest.

Every generated test sends one real API call and asserts the exact status, the
error key, the response schema (tests/team/api/contract.py) and the stored state.

Written next to the output, except for --demo-env modules:
  generated_cases.json  the case manifest (operation, input, constraint, class or
                        boundary point, request, fixture, expected result, test id)
  api_contract.json     the spec's operations with $refs resolved, for the contract
                        tests (the test environment has no YAML parser)

--demo-env NAME=VALUE makes the generated module load its tests only when the
environment variable NAME equals VALUE. The constraint-change demonstrations use
it: they are expected to fail against the unchanged app and must not break normal
suite discovery.
"""

import argparse
import datetime as dt
import hashlib
import itertools
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment message
    sys.exit("PyYAML is required: pip install -r scripts/sqe/requirements-generator.txt "
             "(any virtual environment), or use a Python that has 'yaml'.")

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC = "docs/sqe/openapi/leaveflow-api.yaml"
DEFAULT_OUTPUT = "tests/team/generated/test_generated_api.py"
MANIFEST_NAME = "generated_cases.json"
CONTRACT_NAME = "api_contract.json"
GENERATOR = "scripts/sqe/generate_api_tests.py"

METHODS = ("get", "post", "put", "patch", "delete")
OUT_OF_ENUM = "zzz_not_in_enum"
FILL_CHAR = "n"  # non-whitespace, so trimming does not change the length
INVALID_FORMAT = {"date": "not-a-date", "date-time": "not-a-datetime"}
WRONG_TYPE = {  # a JSON value of another type that DRF does not coerce
    "string": True,
    "integer": "not-a-number",
    "number": "not-a-number",
    "boolean": "not-a-boolean",
    "array": "not-an-array",
    "object": "not-an-object",
}
# Fixture names the generated harness provides (see HARNESS below).
FIXTURE_ROOTS = {"e1", "e2", "m1", "m2", "admin", "teamless_manager", "password",
                 "pending", "approved", "rejected", "other_team", "own"}
READBACKS = {"created", "decided", "token", "none"}


class SpecError(Exception):
    pass


class Missing:
    """Marker: the field is omitted from the request body."""


MISSING = Missing()


class Fixture:
    """Marker: the value comes from a fixture at test time."""

    def __init__(self, ref):
        self.ref = ref


# ---------------------------------------------------------------------------
# Spec reading
# ---------------------------------------------------------------------------
def resolve(spec, node, seen=()):
    """Follow local $ref pointers ("#/components/schemas/X")."""
    while isinstance(node, dict) and "$ref" in node:
        ref = node["$ref"]
        if not ref.startswith("#/") or ref in seen:
            raise SpecError(f"Unsupported or cyclic $ref: {ref}")
        seen = (*seen, ref)
        node = spec
        for part in ref[2:].split("/"):
            node = node[part]
    return node


def deref(spec, node):
    """Copy of node with every local $ref replaced by its target (no recursion support)."""
    node = resolve(spec, node)
    if isinstance(node, dict):
        return {k: deref(spec, v) for k, v in node.items()}
    if isinstance(node, list):
        return [deref(spec, v) for v in node]
    return node


def json_body(spec, operation):
    """(schema, example, media types) of the request body, or (None, {}, [])."""
    if not operation.get("requestBody"):
        return None, {}, []
    content = resolve(spec, operation["requestBody"])["content"]
    media = content["application/json"]
    schema = resolve(spec, media["schema"])
    example = media.get("example", schema.get("example"))
    if schema.get("type") != "object" or not isinstance(example, dict):
        raise SpecError("A JSON object schema with an example body is required for generation.")
    return schema, example, list(content)


def documented_codes(operation):
    codes = sorted(int(code) for code in operation["responses"] if str(code).isdigit())
    success = [c for c in codes if 200 <= c < 300]
    if len(success) != 1:
        raise SpecError(f"{operation.get('operationId')}: exactly one 2xx response is required.")
    return success[0], [c for c in codes if 400 <= c < 500]


def check_ref(ref, where):
    if not isinstance(ref, str) or ref.split(".")[0] not in FIXTURE_ROOTS:
        raise SpecError(f"{where}: unknown fixture reference {ref!r}; known roots: {sorted(FIXTURE_ROOTS)}")
    return ref


def response_contract(spec, sha):
    operations = {}
    for path, item in spec["paths"].items():
        for method in METHODS:
            if method not in item:
                continue
            op = item[method]
            schema, _, media = json_body(spec, op)
            operations[op["operationId"]] = {
                "method": method,
                "path": path,
                "secured": bool(op.get("security", spec.get("security"))),
                "parameters": [p["name"] for p in op.get("parameters", [])],
                "request_media": media,
                "request_fields": {
                    name: resolve(spec, field).get("enum")
                    for name, field in (schema or {}).get("properties", {}).items()
                },
                "responses": {
                    str(code): {
                        kind: deref(spec, content["schema"])
                        for kind, content in resolve(spec, response)["content"].items()
                    }
                    for code, response in op["responses"].items()
                },
            }
    return {"generated_by": GENERATOR, "spec_sha256": sha, "operations": operations,
            "flows": spec.get("x-operation-flows", [])}


# ---------------------------------------------------------------------------
# Case derivation
# ---------------------------------------------------------------------------
class Case:
    """One class or boundary point of one input.

    where: body | rule | path | context | auth | media | method. status overrides
    the expectation that follows from ``valid`` and ``where``.
    """

    def __init__(self, field, technique, label, value, valid, *, constraint, where="body", status=None):
        self.field, self.technique, self.label = field, technique, label
        self.value, self.valid = value, valid
        self.constraint, self.where, self.status = constraint, where, status


def shift(value, fmt, delta):
    if fmt == "date":
        return (dt.date.fromisoformat(value) + dt.timedelta(days=delta)).isoformat()
    if fmt == "date-time":
        return (dt.datetime.fromisoformat(value) + dt.timedelta(seconds=delta)).isoformat()
    return value + delta


def value_text(value):
    return value if isinstance(value, str) else json.dumps(value)


def bva(field, limit, label, expected, *, constraint, fmt=None, step=1, floor=None, convert=lambda v: v, where="body"):
    """limit-1, limit, limit+1 with expected = (below, at, above) validity."""
    cases = []
    for point, delta, valid in zip(("limit-1", "limit", "limit+1"), (-step, 0, step), expected):
        value = shift(limit, fmt, delta)
        if floor is not None and value < floor:
            continue  # infeasible point, listed by not_applicable()
        cases.append(Case(field, "BVA", f"{value_text(value)} ({point}, {label})", convert(value), valid,
                          constraint=constraint, where=where))
    return cases


def length(n):
    return FILL_CHAR * n


def field_cases(name, schema, required, example, binding):
    typ, fmt = schema.get("type"), schema.get("format")
    if typ not in WRONG_TYPE:
        raise SpecError(f"Field {name}: unsupported or missing type {typ!r}")
    cases = []

    def ep(label, value, valid, constraint):
        cases.append(Case(name, "EP", label, value, valid, constraint=constraint))

    if "enum" in schema:
        for option in schema["enum"]:
            ep(f"valid enum value {option!r}", option, True, "enum")
        ep(f"invalid out-of-enum {OUT_OF_ENUM!r}", OUT_OF_ENUM, False, "enum")
    else:
        nominal = Fixture(binding) if binding else example.get(name, schema.get("default"))
        if nominal is None:
            raise SpecError(f"Field {name}: no example, default or binding to use as the valid value")
        ep(f"valid {typ}" + (f" ({fmt})" if fmt else ""), nominal, True, "type")
    ep(f"invalid wrong type ({json.dumps(WRONG_TYPE[typ])})", WRONG_TYPE[typ], False, "type")
    if fmt in INVALID_FORMAT:
        ep(f"invalid {fmt} format ({INVALID_FORMAT[fmt]!r})", INVALID_FORMAT[fmt], False, "format")
    if schema.get("nullable", False):
        ep("valid null (nullable)", None, True, "nullable")
    else:
        ep("invalid null (not nullable)", None, False, "nullable")
    if required:
        ep("invalid missing (required)", MISSING, False, "required")
    else:
        ep("valid omitted (optional)", MISSING, True, "required")
    for value in schema.get("x-invalid-examples", []):
        ep(f"invalid example {value!r}", value, False, "x-invalid-examples")

    for keyword in ("maxLength", "x-trimmed-max-length"):
        if keyword in schema:
            limit = int(schema[keyword])
            ep(f"invalid over {keyword} ({2 * limit} chars)", length(2 * limit), False, keyword)
            cases += bva(name, limit, f"{keyword} {limit}", (True, True, False), constraint=keyword,
                         floor=0, convert=length)
    if "x-trimmed-max-length" in schema:
        limit = int(schema["x-trimmed-max-length"])
        ep("valid whitespace only", "   ", True, "x-trimmed-max-length")
        ep(f"valid padded {limit} chars after trim", f" {length(limit)} ", True, "x-trimmed-max-length")
        ep(f"invalid padded {limit + 1} chars after trim", f" {length(limit + 1)} ", False, "x-trimmed-max-length")
    if "minLength" in schema:
        limit = int(schema["minLength"])
        cases += bva(name, limit, f"minLength {limit}", (False, True, True), constraint="minLength",
                     floor=0, convert=length)

    step = 1 if typ == "integer" else schema.get("x-step", 0.01)
    if "minimum" in schema:
        cases += bva(name, schema["minimum"], f"minimum {schema['minimum']}",
                     (False, not schema.get("exclusiveMinimum", False), True), constraint="minimum", step=step)
    if "maximum" in schema:
        cases += bva(name, schema["maximum"], f"maximum {schema['maximum']}",
                     (True, not schema.get("exclusiveMaximum", False), False), constraint="maximum", step=step)
    rel = schema.get("x-relational")
    if rel:
        other, op = rel["field"], rel["operator"]
        expected = {">=": (False, True, True), ">": (False, False, True),
                    "<=": (True, True, False), "<": (True, False, False)}.get(op)
        if expected is None or other not in example:
            raise SpecError(f"Field {name}: x-relational needs an operator and a field present in the example")
        cases += bva(name, example[other], f"{name} {op} {other}", expected, constraint="x-relational",
                     fmt=fmt if fmt in {"date", "date-time"} else None)
    return cases


def end_after_business_days(start, days):
    """Last day of an interval from start that contains exactly ``days`` weekdays."""
    current, counted = dt.date.fromisoformat(start), 0
    while True:
        counted += current.weekday() < 5
        if counted == days:
            return current.isoformat()
        current += dt.timedelta(days=1)


def rule_cases(rule, fixture):
    """Cases of one x-rule-boundaries entry; the input is the interval 'first..last'."""
    first, last = rule["fields"]
    name, rid, where = f"{first}..{last}", rule["rule"], {"where": "rule", "constraint": f"x-rule-boundaries {rule['rule']}"}
    if rule["kind"] == "business-days":
        limit, start = fixture[rule["maximum"]], rule["start"]

        def interval(days):
            return {first: start, last: end_after_business_days(start, days)}
        cases = bva(name, limit, f"{rid} business days <= {limit}", (True, True, False), convert=interval, **where)
        return cases + [Case(name, "EP", f"invalid {rid} {2 * limit} business days", interval(2 * limit), False, **where)]
    if rule["kind"] == "interval-overlap":
        existing = fixture[rule["interval"]]
        multi = existing["start"] != existing["end"]

        def one_day(day):
            return {first: day, last: day}
        cases = bva(name, existing["start"], f"{rid} existing start", (True, False, not multi),
                    fmt="date", convert=one_day, **where)
        cases += bva(name, existing["end"], f"{rid} existing end", (not multi, False, True),
                     fmt="date", convert=one_day, **where)
        around = {first: shift(existing["start"], "date", -1), last: shift(existing["end"], "date", 1)}
        return cases + [Case(name, "EP", f"invalid {rid} encloses existing", around, False, **where)]
    raise SpecError(f"Unknown x-rule-boundaries kind {rule['kind']!r}")


class Operation:
    def __init__(self, spec, path, method, op, undocumented):
        self.path, self.method, self.op_id = path, method, op["operationId"]
        self.endpoint = f"{method.upper()} {path}"
        self.schema, example, self.media = json_body(spec, op)
        self.success, self.errors = documented_codes(op)
        meta = op.get("x-sqe-test")
        if meta is None:
            raise SpecError(f"{self.endpoint}: x-sqe-test is required for generation")
        self.actor = meta.get("actor")
        if self.actor is not None:
            check_ref(self.actor, f"{self.endpoint} actor")
        self.readback = meta["readback"]
        if self.readback not in READBACKS:
            raise SpecError(f"{self.endpoint}: readback must be one of {sorted(READBACKS)}")
        self.invalid_status, self.error_key = meta.get("invalid_status"), meta.get("error_key", "detail")
        if self.schema and (self.invalid_status not in self.errors or self.error_key not in {"field", "detail"}):
            raise SpecError(f"{self.endpoint}: invalid_status must be documented and error_key field|detail")
        bindings = {k: check_ref(v, f"{self.endpoint} binding {k}") for k, v in meta.get("bindings", {}).items()}
        self.path_params = {k: check_ref(v, f"{self.endpoint} path {k}") for k, v in meta.get("path_params", {}).items()}
        if set(re.findall(r"{(\w+)}", path)) - set(self.path_params):
            raise SpecError(f"{self.endpoint}: every path parameter needs x-sqe-test.path_params")
        self.base = {k: Fixture(bindings[k]) if k in bindings else v for k, v in example.items()}
        self.defaults, self.inputs, self.not_applicable = {}, [], []

        props = {k: resolve(spec, v) for k, v in (self.schema or {}).get("properties", {}).items()}
        required = set((self.schema or {}).get("required", []))
        for name, schema in props.items():
            if "default" in schema:
                self.defaults[name] = schema["default"]
            self.add(name, field_cases(name, schema, name in required, example, bindings.get(name)))
            self.explain(name, schema)
        rules = {}
        for rule in op.get("x-rule-boundaries", []):
            for case in rule_cases(rule, spec["x-sqe-fixture"]):
                rules.setdefault(case.field, []).append(case)
        for name, cases in rules.items():
            self.add(name, cases)
        for parameter in op.get("parameters", []):
            if parameter["in"] != "path":
                raise SpecError(f"{self.endpoint}: only path parameters are supported")
            name = parameter["name"]
            self.add(name, [Case(name, "EP", "valid existing record", MISSING, True, constraint="type", where="path")]
                     + [Case(name, "EP", f"invalid example {v!r}", v, False, constraint="x-invalid-examples", where="path")
                        for v in parameter.get("x-invalid-examples", [])])
            self.skip(name, "BVA", "Record identity is not an ordered limit; the spec documents no minimum or maximum.")
        contexts = [self.context_case(c) for c in op.get("x-context-cases", [])]
        if contexts:
            self.add("context", contexts)
            self.skip("context", "BVA", "Actor, role and record state are unordered categories.")
        if op.get("security", spec.get("security")):
            self.add("Authorization", [
                Case("Authorization", "EP", label, value, value == "actor", constraint="security", where="auth")
                for label, value in (("valid token", "actor"), ("invalid no token", "none"), ("invalid unknown token", "invalid"))
            ])
            self.skip("Authorization", "BVA", "An opaque token has no ordered limit.")
        if self.schema:
            self.add("media", [Case("media", "EP", f"valid {m}", (m, None), True, constraint="requestBody.content", where="media")
                               for m in self.media] + [
                Case("media", "EP", "invalid malformed JSON", ("application/json", "{"), False,
                     constraint="requestBody.content", where="media", status=400),
                Case("media", "EP", "invalid text/plain", ("text/plain", "x"), False,
                     constraint="requestBody.content", where="media", status=415)])
        if undocumented:
            self.add("method", [Case("method", "EP", f"invalid {m.upper()}", m, False, constraint="paths", where="method", status=405)
                                for m in undocumented])
            self.skip("method", "EP", "HEAD and OPTIONS are provided by the framework and are outside the selected scope.")
        if not self.inputs:
            raise SpecError(f"{self.endpoint}: nothing to generate")
        self.tests = self.merge()

    def add(self, name, cases):
        self.inputs.append((name, cases))

    def skip(self, name, technique, reason):
        self.not_applicable.append({"endpoint": self.endpoint, "input": name, "technique": technique, "reason": reason})

    def explain(self, name, schema):
        """Record why BVA (or one of its points) does not apply to a body field."""
        bounded = {"maxLength", "minLength", "x-trimmed-max-length", "minimum", "maximum", "x-relational"} & set(schema)
        if "enum" in schema:
            self.skip(name, "BVA", "Enum values are unordered.")
        elif not bounded:
            self.skip(name, "BVA", "The spec documents no ordered limit for this field.")
        if schema.get("minLength") == 0:
            self.skip(name, "BVA point -1", "A length below 0 is infeasible.")

    def context_case(self, entry):
        actor = check_ref(entry["actor"], f"{self.endpoint} context")
        target = {k: Fixture(check_ref(v, f"{self.endpoint} context")) for k, v in entry.get("path", {}).items()}
        status = entry["status"]
        if status != self.success and status not in self.errors:
            raise SpecError(f"{self.endpoint}: context status {status} is not documented")
        valid = status == self.success
        return Case("context", "EP", f"{'valid' if valid else 'invalid'} {entry['name']}", (actor, target), valid,
                    constraint="x-context-cases", where="context", status=status)

    def request(self, case):
        request = {"body": dict(self.base), "path": {}, "auth": "actor", "actor": self.actor,
                   "method": self.method, "media": "application/json", "raw": None}
        if case.where == "auth":
            request["auth"] = case.value
        elif case.where == "path":
            if case.value is not MISSING:
                request["path"] = {case.field: case.value}
        elif case.where == "context":
            request["actor"], request["path"] = case.value
        elif case.where == "media":
            request["media"], request["raw"] = case.value
        elif case.where == "method":
            request["method"] = case.value
        elif case.where == "rule":
            request["body"].update(case.value)
        elif case.value is MISSING:
            request["body"].pop(case.field, None)
        else:
            request["body"][case.field] = case.value
        # A target equal to the operation's own one is the base request.
        if {k: v.ref for k, v in request["path"].items() if isinstance(v, Fixture)} == self.path_params:
            request["path"] = {}
        return request

    def expectation(self, case):
        """(status, error key) of a case."""
        if case.valid:
            return self.success, None
        status = case.status or {"path": 404, "auth": 401}.get(case.where, self.invalid_status)
        if case.where != "method" and status not in self.errors:
            raise SpecError(f"{self.endpoint}: {status} is not a documented response")
        if case.where == "rule":
            return status, "non_field_errors"
        if case.where == "body":
            return status, case.field if self.error_key == "field" else "detail"
        # An id that is no non-negative integer gets the HTML 404, which has no error key.
        return status, None if case.where == "path" else "detail"

    def merge(self):
        merged, used = {}, set()
        for case in itertools.chain.from_iterable(cases for _, cases in self.inputs):
            request, expected = self.request(case), self.expectation(case)
            key = json.dumps(request, sort_keys=True, default=lambda v: {"$fixture": v.ref})
            if key in merged and merged[key]["expected"] != expected:
                raise SpecError(f"{self.endpoint}: contradictory expectations for {key}")
            if key not in merged:
                merged[key] = {**request, "expected": expected, "cases": [], "name": test_name(case, used)}
            merged[key]["cases"].append(case)
        return list(merged.values())


def load_operations(spec):
    ops = []
    for path, item in spec["paths"].items():
        documented = [m for m in METHODS if m in item]
        for n, method in enumerate(documented):
            # A path's undocumented methods are generated once, with its first operation.
            undocumented = [m for m in METHODS if m not in documented] if n == 0 else []
            ops.append(Operation(spec, path, method, item[method], undocumented))
    return ops


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def py(value):
    if isinstance(value, Fixture):
        return f"F({value.ref!r})"
    if isinstance(value, str) and len(value) > 40:
        runs = [(c, len(list(g))) for c, g in itertools.groupby(value)]
        if len(runs) <= 3:
            return " + ".join(repr(c) if n == 1 else f"{c!r} * {n}" for c, n in runs)
    return repr(value)


def dict_source(values):
    return "{" + ", ".join(f"{k!r}: {py(v)}" for k, v in values.items()) + "}"


def ident(text):
    text = text.replace("''", "empty").replace(" -", " minus ")
    return re.sub(r"[^0-9a-zA-Z]+", "_", text).strip("_").lower() or "x"


def test_name(case, used):
    if case.technique == "BVA":
        value, point = case.label.split(" (", 1)
        point, rest = point.rstrip(")").split(", ", 1)
        point = {"limit-1": "below", "limit": "at", "limit+1": "above"}[point]
        base = f"test_{ident(case.field)}_bva_{ident(value)}_{point}" + (f"_{ident(rest)}" if case.where == "rule" else "")
    else:
        base = f"test_{ident(case.field)}_ep_{ident(case.label)}"
    base = base[:90].rstrip("_")
    name, n = base, 2
    while name in used:
        name, n = f"{base}_{n}", n + 1
    used.add(name)
    return name


def class_name(op):
    return "Generated" + op.op_id[0].upper() + op.op_id[1:] + "Tests"


def call_source(op, test):
    status, error = test["expected"]
    args = [dict_source(test["body"]), f"status={status}"]
    if test["path"]:
        args.append(f"path={dict_source(test['path'])}")
    for key, default in (("auth", "actor"), ("actor", op.actor), ("method", op.method),
                         ("media", "application/json"), ("raw", None)):
        if test[key] != default:
            args.append(f"{key}={test[key]!r}")
    if error:
        args.append(f"error={error!r}")
    return ", ".join(args)


def manifest(ops, sha, source, fixture):
    def shown(v):
        if isinstance(v, Fixture):
            return {"fixture": v.ref}
        if isinstance(v, str) and len(v) > 40:
            return {"runs": [[c, len(list(g))] for c, g in itertools.groupby(v)]}
        return v

    def visible(values):
        return {k: shown(v) for k, v in values.items()}
    cases = [{
        "id": f"tests.team.generated.test_generated_api.{class_name(op)}.{test['name']}",
        "operation": op.op_id,
        "endpoint": op.endpoint,
        "classes": [{"input": c.field, "technique": c.technique, "class": c.label, "constraint": c.constraint,
                     "valid": c.valid} for c in test["cases"]],
        "request": {"method": test["method"], "path": visible(test["path"]), "body": visible(test["body"]),
                    "auth": test["auth"], "actor": test["actor"], "media": test["media"], "raw": test["raw"]},
        "expected": {"status": test["expected"][0], "error_key": test["expected"][1],
                     "readback": op.readback if test["expected"][0] == op.success else "unchanged"},
    } for op in ops for test in op.tests]
    return {"generated_by": GENERATOR, "spec_sha256": sha, "seed": "none (deterministic)", "fixture": fixture,
            "module_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(), "cases": cases,
            "not_applicable": [entry for op in ops for entry in op.not_applicable]}


HARNESS = '''
class F:
    """Fixture-bound value, resolved inside the test."""

    def __init__(self, ref):
        self.ref = ref


class GeneratedApiTestCase(TestCase):
    """Runtime harness emitted by the generator; uses the A2.1 fixtures and token clients."""

    OPERATION = METHOD = PATH = READBACK = ACTOR = None
    PATH_PARAMS = {}
    DEFAULTS = {}
    SUCCESS = 200

    def setUp(self):
        # x-sqe-fixture: every allowance, and e1's pending request (W2 target, overlap interval).
        self.people = p = build_people("gen", allowance=FIXTURE["allowance"])
        start, end = (date.fromisoformat(FIXTURE["pending"][k]) for k in ("start", "end"))
        self.records = {
            "pending": make_request(p.e1, start=start, end=end),
            "approved": make_request(p.e2, start=date(2026, 12, 21), end=date(2026, 12, 22),
                                     status=LeaveRequest.Status.APPROVED, decided_by=p.m1),
            "rejected": make_request(p.e2, start=date(2026, 12, 23), end=date(2026, 12, 23),
                                     status=LeaveRequest.Status.REJECTED, decided_by=p.m1),
            "other_team": make_request(p.m2, start=start, end=end),
            "own": make_request(p.m1, start=start, end=end),
        }

    def ref(self, ref):
        root, *attrs = ref.split(".")
        value = TEST_PASSWORD if root == "password" else self.records.get(root) or getattr(self.people, root)
        for attr in attrs:
            value = getattr(value, attr)
        return value

    def resolve(self, values):
        return {k: self.ref(v.ref) if isinstance(v, F) else v for k, v in values.items()}

    def client_for(self, auth, actor):
        if auth == "actor" and actor:
            return token_client(self.ref(actor))
        client = APIClient()
        if auth == "invalid":
            client.credentials(HTTP_AUTHORIZATION="Token " + "0" * 40)
        return client

    def balances(self):
        return {user.pk: balance_view(user) for user in vars(self.people).values() if hasattr(user, "role")}

    def state(self):
        return all_rows(), self.balances(), set(Token.objects.values_list("key", flat=True))

    def send(self, client, method, url, body, media, raw):
        call = getattr(client, method)
        if method == "get":
            return call(url)
        if raw is not None:
            return call(url, raw, content_type=media)
        if media == "application/json":
            return call(url, body, format="json")
        if media == "multipart/form-data":
            return call(url, body, format="multipart")
        return call(url, urlencode(body), content_type=media)

    def check(self, body, *, status, path=None, auth="actor", actor=None, method=None,
              media="application/json", raw=None, error=None):
        """One real API call; assert exact status, error key, response schema and stored state."""
        actor, method = actor or self.ACTOR, method or self.METHOD
        client, body = self.client_for(auth, actor), self.resolve(body)
        target = {**{k: self.ref(v) for k, v in self.PATH_PARAMS.items()}, **self.resolve(path or {})}
        before, started = self.state(), timezone.now()
        response = self.send(client, method, self.PATH.format(**target), body, media, raw)
        data = getattr(response, "data", None)
        shown = "(login response hidden)" if self.READBACK == "token" else repr(data)
        self.assertEqual(response.status_code, status, f"{method.upper()} {self.PATH}, expected {status}: {shown}")
        if status != 405:  # OpenAPI documents implemented methods only
            self.assertEqual(response_errors(self.OPERATION, response), [])
        if error is not None:
            self.assertEqual(set(data), {error}, shown)
        after = self.state()
        if status == self.SUCCESS and self.READBACK != "none":
            getattr(self, "assert_" + self.READBACK)(body, before, after, response, actor, target, started)
        else:
            self.assertTrue(after == before, "a refused or read-only call changed stored state")

    def assert_created(self, body, before, after, response, actor, target, started):
        """Exactly one new row, as submitted, pending and owned by the caller; nothing else changed."""
        expected = {**self.DEFAULTS, **body}
        new = [row for row in after[0] if row not in before[0]]
        self.assertEqual((len(new), len(after[0])), (1, len(before[0]) + 1))
        row = new[0]
        self.assertEqual(
            (row["id"], row["employee_id"], row["status"], row["decided_by_id"], row["decided_at"]),
            (response.json()["id"], self.ref(actor).pk, LeaveRequest.Status.PENDING, None, None),
        )
        self.assertEqual(
            (row["leave_type"], row["start_date"].isoformat(), row["end_date"].isoformat(), row["note"]),
            (expected["leave_type"], expected["start_date"], expected["end_date"], expected["note"].strip()),
        )
        self.assertTrue(after[1:] == before[1:], "balance or tokens changed")

    def assert_decided(self, body, before, after, response, actor, target, started):
        """Same row and content, new status, decider and time; only the owner's balance moves, on approval."""
        old = next(row for row in before[0] if row["id"] == target["id"])
        new = next(row for row in after[0] if row["id"] == target["id"])
        self.assertEqual(response.json()["id"], target["id"])
        self.assertTrue(started <= new["decided_at"] <= timezone.now())
        self.assertEqual(new, {**old, "status": body["status"], "decided_by_id": self.ref(actor).pk,
                               "decided_at": new["decided_at"]})
        self.assertEqual([r for r in after[0] if r["id"] != target["id"]], [r for r in before[0] if r["id"] != target["id"]])
        days = LeaveRequest.objects.get(pk=target["id"]).business_days if body["status"] == "approved" else 0
        allowance, used, available = before[1][old["employee_id"]]
        self.assertEqual(after[1], {**before[1], old["employee_id"]: (allowance, used + days, available - days)})
        self.assertTrue(after[2] == before[2], "tokens changed")

    def assert_token(self, body, before, after, response, actor, target, started):
        """One token, returned by the call and bound to the user who logged in; requests unchanged."""
        created = after[2] - before[2]
        self.assertTrue(created == {response.json()["token"]}, "the returned token is the only new one")
        user = Token.objects.get(key=created.pop()).user
        self.assertEqual((user.username, response.json()["user"]["id"]), (body["username"], user.pk))
        self.assertTrue(after[:2] == before[:2], "requests or balances changed")
'''


def render(spec_label, sha, ops, demo_env, command, fixture):
    lines = [
        "# =============================================================================",
        "# GENERATED FILE - DO NOT EDIT BY HAND.",
        f"# Generator: {GENERATOR}",
        f"# Spec:      {spec_label}",
        f"# Spec SHA-256: {sha}",
        f"# Command:   {command}",
        "#",
        "# One input varies per test; the rest is the operation's example request.",
        "# EP and 3-point BVA classes: see the generator's module docstring. Identical",
        "# requests are generated once; the docstring lists every class the test covers",
        "# (count each executable case once).",
        f"# Tests: {sum(len(op.tests) for op in ops)}",
    ]
    if demo_env:
        lines += [
            "#",
            f"# DEMONSTRATION MODULE: its tests load only when {demo_env[0]}={demo_env[1]}.",
            "# It encodes a changed spec and is expected to fail against the unchanged",
            "# application; normal discovery of tests.team loads no tests from it.",
        ]
    lines += [
        "# =============================================================================",
        '"""OpenAPI-generated EP/BVA API tests (A2.4). Regenerate instead of editing."""',
        "",
        *(["import os"] if demo_env else []),
        "from datetime import date",
        "from urllib.parse import urlencode",
        "",
        "from django.test import TestCase",
        "from django.utils import timezone",
        "from rest_framework.authtoken.models import Token",
        "from rest_framework.test import APIClient",
        "",
        "from leave.models import LeaveRequest",
        "from tests.team.api.contract import response_errors",
        "from tests.team.api.support import all_rows, balance_view, token_client",
        "from tests.team.fixtures.leave_data import TEST_PASSWORD, build_people, make_request",
        "",
        f"SPEC_SHA256 = {sha!r}",
        f"FIXTURE = {fixture!r}",
    ]
    if demo_env:
        lines += [
            f"DEMO_ENABLED = os.environ.get({demo_env[0]!r}) == {demo_env[1]!r}",
            "",
            "",
            "def load_tests(loader, tests, pattern):",
            '    """Load this demonstration module\'s tests only when explicitly enabled."""',
            "    return tests if DEMO_ENABLED else loader.suiteClass()",
        ]
    lines += ["", "", HARNESS.strip("\n")]
    for op in ops:
        lines += [
            "",
            "",
            f"class {class_name(op)}(GeneratedApiTestCase):",
            f'    """{op.endpoint}: {len(op.tests)} generated tests."""',
            "",
            f"    OPERATION = {op.op_id!r}",
            f"    METHOD = {op.method!r}",
            f"    PATH = {op.path!r}",
            f"    ACTOR = {op.actor!r}",
            f"    PATH_PARAMS = {op.path_params!r}",
            f"    DEFAULTS = {op.defaults!r}",
            f"    READBACK = {op.readback!r}",
            f"    SUCCESS = {op.success!r}",
        ]
        for test in op.tests:
            first, *others = test["cases"]
            status, error = test["expected"]
            lines += ["", f"    def {test['name']}(self):",
                      f'        """Generated from spec: {op.endpoint} {first.field} {first.technique} {first.label}', ""]
            lines += [f"        Also generated from spec: {op.endpoint} {c.field} {c.technique} {c.label}" for c in others]
            if others:
                lines.append("")
            lines += [f"        Expect {status}" + (f", error key {error}." if error else "."), '        """',
                      f"        self.check({call_source(op, test)})"]
    return "\n".join(lines) + "\n"


def summary(ops):
    out = []
    for op in ops:
        out.append(f"Endpoint: {op.endpoint}")
        for name, cases in op.inputs:
            ep = [c for c in cases if c.technique == "EP"]
            out.append(f"{name}: {sum(c.valid for c in ep)} valid EP, {sum(not c.valid for c in ep)} invalid EP")
            points = [c.label.split(" (")[0] for c in cases if c.technique == "BVA"]
            if points:
                out.append(f"{name}: {len(points)} BVA values ({', '.join(points)})")
        out.append(f"-> {sum(len(c) for _, c in op.inputs)} cases, {len(op.tests)} tests after merging identical requests")
        out.append("")
    out.append(f"Total: {sum(len(op.tests) for op in ops)} tests generated")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("spec", nargs="?", default=DEFAULT_SPEC, help="OpenAPI YAML path (relative to the repo root or absolute)")
    parser.add_argument("--patch", metavar="FILE", help="unified diff applied to the spec in memory before generating")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="generated test module path")
    parser.add_argument("--demo-env", metavar="NAME=VALUE", help="load the generated tests only when NAME=VALUE")
    args = parser.parse_args(argv)
    demo_env = None
    if args.demo_env:
        name, sep, value = args.demo_env.partition("=")
        if not sep or not re.fullmatch(r"[A-Z][A-Z0-9_]*", name) or not value:
            parser.error("--demo-env must look like NAME=VALUE")
        demo_env = (name, value)
    if args.patch and not demo_env:
        parser.error("--patch is for demonstrations: pass --demo-env (and an --output of its own) as well")
    if demo_env and args.output == DEFAULT_OUTPUT:
        parser.error("--demo-env needs its own --output; the baseline module must stay the baseline")

    spec_file = ROOT / args.spec  # an absolute path replaces ROOT
    if args.patch:
        done = subprocess.run(["patch", "--silent", "--fuzz=0", "-o", "-", str(spec_file), str(ROOT / args.patch)],
                              capture_output=True, text=True, encoding="utf-8")
        if done.returncode:
            sys.exit(f"Patch does not apply: {done.stdout}{done.stderr}")
        spec_text = done.stdout
    else:
        spec_text = spec_file.read_text(encoding="utf-8")
    spec = yaml.safe_load(spec_text)
    if not str(spec.get("openapi", "")).startswith("3.0"):
        parser.error("Only OpenAPI 3.0 documents are supported")
    try:
        ops = load_operations(spec)
    except (SpecError, KeyError, TypeError, ValueError) as exc:
        sys.exit(f"Spec error: {exc!r}")

    sha = hashlib.sha256(spec_text.encode("utf-8")).hexdigest()
    command = ["python3", GENERATOR, args.spec]
    for option, value in (("--patch", args.patch), ("--output", args.output), ("--demo-env", args.demo_env)):
        command += [option, value] if value else []
    label = args.spec + (f" + {args.patch}" if args.patch else "")
    source = render(label, sha, ops, demo_env, " ".join(command), spec["x-sqe-fixture"])
    out_file = ROOT / args.output
    compile(source, str(out_file), "exec")  # fail before writing if the output is not valid Python

    out_file.parent.mkdir(parents=True, exist_ok=True)
    init = out_file.parent / "__init__.py"
    if not init.exists():
        init.write_text('"""Generated API tests."""\n', encoding="utf-8")
    out_file.write_text(source, encoding="utf-8")
    if not demo_env:
        for name, value in ((CONTRACT_NAME, response_contract(spec, sha)),
                            (MANIFEST_NAME, manifest(ops, sha, source, spec["x-sqe-fixture"]))):
            (out_file.parent / name).write_text(json.dumps(value, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(summary(ops))
    print(f"Written: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
