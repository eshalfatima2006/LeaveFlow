#!/usr/bin/env python3
"""Generate EP/BVA API tests from the LeaveFlow OpenAPI specification (A2.4).

Usage:
    python3 scripts/sqe/generate_api_tests.py [SPEC] [--output PATH] [--demo-env NAME=VALUE]

SPEC defaults to docs/sqe/openapi/leaveflow-api.yaml and --output to
tests/team/generated/test_generated_api.py. Requires PyYAML (the project .venv
does not ship it; any Python 3 with PyYAML can run the generator, since it
only reads YAML and writes Python source).

For every POST operation with a JSON request body, the generator reads each
input (body field, path parameter, Authorization header) from the spec and derives:

  EP, valid     one class per enum value; otherwise one class for the declared
                type/format (value: the request example or an x-sqe-test binding);
                an omitted optional field
  EP, invalid   wrong type; out-of-enum (enum fields); invalid format
                (date/date-time); null (unless nullable); missing (required
                fields); over-max-length (2 x maxLength characters); every
                x-invalid-examples value; no token and an unknown token (secured
                operations)
  BVA           3 points limit-1, limit, limit+1 for maxLength, minLength,
                minimum, maximum, x-relational date comparisons and
                x-rule-boundaries (business days vs allowance, both ends of the
                fixture's existing interval); a length below 0 is infeasible

Each case changes one input of the operation's example request (an
x-rule-boundaries case sets its start/end pair, which is one interval input).
Cases that yield the same request are merged into one test (the docstring lists
every class the test covers); the same request with contradictory expectations
aborts generation. The generated module sends each request through one real API
call with the spec's fixture actor, asserts the exact documented status (valid ->
2xx, invalid body -> x-sqe-test.invalid_status, path -> 404, token -> 401), the
error key, and the persisted outcome named by x-sqe-test.readback.

generated_cases.json, written next to the output, is the case manifest: one entry
per generated test with its classes, request and expected status.

The documented response schemas of every operation are also exported, with
$refs resolved, to api_contract.json next to the output. The contract tests read
that JSON, because the test environment has no YAML parser.

--demo-env NAME=VALUE makes the generated module load its tests only when
the environment variable NAME equals VALUE. It is used for the constraint-change
demonstrations (v2, v3), which are expected to fail against the unchanged app
and must not break normal suite discovery.
"""

import argparse
import datetime as dt
import hashlib
import json
import keyword
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment message
    sys.exit("PyYAML is required: run with a Python that has 'yaml' installed (e.g. system python3).")

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC = "docs/sqe/openapi/leaveflow-api.yaml"
DEFAULT_OUTPUT = "tests/team/generated/test_generated_api.py"
MANIFEST_NAME = "generated_cases.json"
CONTRACT_NAME = "api_contract.json"  # written next to the output, except for --demo-env modules
GENERATOR = "scripts/sqe/generate_api_tests.py"

OUT_OF_ENUM = "zzz_not_in_enum"
FILL_CHAR = "n"  # non-whitespace, so DRF trimming does not change the length
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
FIXTURE_ROOTS = {"e1", "e2", "m1", "m2", "admin", "teamless_manager", "pending", "password"}
READBACKS = {"created", "decided", "token"}


class SpecError(Exception):
    pass


class Missing:
    """Marker: the field is omitted from the request body."""

    def __repr__(self):
        return "MISSING"


MISSING = Missing()


class Fixture:
    """Marker: the value comes from a fixture at test time (x-sqe-test.bindings)."""

    def __init__(self, ref):
        self.ref = ref

    def __eq__(self, other):
        return isinstance(other, Fixture) and other.ref == self.ref

    def __hash__(self):
        return hash(("fixture", self.ref))


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
        target = spec
        for part in ref[2:].split("/"):
            target = target[part]
        node = target
    return node


def json_body(spec, operation):
    body = operation.get("requestBody")
    if not body:
        return None, None
    media = resolve(spec, body)["content"].get("application/json")
    if not media:
        return None, None
    schema = resolve(spec, media["schema"])
    example = media.get("example", schema.get("example"))
    if schema.get("type") != "object" or not isinstance(example, dict):
        raise SpecError("A JSON object schema with an example body is required for generation.")
    return schema, example


def documented_codes(operation):
    codes = sorted(int(code) for code in operation["responses"] if str(code).isdigit())
    success = [c for c in codes if 200 <= c < 300]
    errors = [c for c in codes if 400 <= c < 500]
    if len(success) != 1 or not errors:
        raise SpecError(f"{operation.get('operationId')}: need exactly one 2xx and at least one 4xx response.")
    return success[0], errors


def check_ref(ref, where):
    if not isinstance(ref, str) or ref.split(".")[0] not in FIXTURE_ROOTS:
        raise SpecError(f"{where}: unknown fixture reference {ref!r}; known roots: {sorted(FIXTURE_ROOTS)}")
    return ref


# ---------------------------------------------------------------------------
# Case derivation
# ---------------------------------------------------------------------------
class Case:
    def __init__(self, field, technique, label, value, valid, where="body"):
        self.field, self.technique, self.label = field, technique, label
        self.value, self.valid = value, valid
        self.where = where  # body | path | auth | rule (value: dict of body fields)


def shift(value, fmt, delta):
    """Step a date/date-time string or a number by delta units."""
    if fmt == "date":
        return (dt.date.fromisoformat(value) + dt.timedelta(days=delta)).isoformat()
    if fmt == "date-time":
        return (dt.datetime.fromisoformat(value) + dt.timedelta(seconds=delta)).isoformat()
    return value + delta


def bva(field, limit, label, valid_at, *, below_valid, above_valid, fmt=None, step=1, floor=None):
    """Three-point BVA: limit-1, limit, limit+1 with the given validity per point."""
    points = []
    for name, delta, valid in (("limit-1", -step, below_valid), ("limit", 0, valid_at), ("limit+1", step, above_valid)):
        value = shift(limit, fmt, delta) if fmt else limit + delta
        if floor is not None and value < floor:
            continue  # infeasible point (e.g. length -1)
        points.append((name, value, valid))
    return [Case(field, "BVA", f"{value_text(v)} ({name}, {label})", v, ok) for name, v, ok in points]


def value_text(value):
    return value if isinstance(value, str) else json.dumps(value)


def field_cases(name, schema, required, base, binding):
    typ = schema.get("type")
    fmt = schema.get("format")
    if typ not in WRONG_TYPE:
        raise SpecError(f"Field {name}: unsupported or missing type {typ!r}")
    nominal = Fixture(binding) if binding else base.get(name, schema.get("default"))
    if nominal is None and "enum" not in schema:
        raise SpecError(f"Field {name}: no example, default or binding to use as the valid value")
    cases = []

    # Equivalence partitions -------------------------------------------------
    if "enum" in schema:
        for option in schema["enum"]:
            cases.append(Case(name, "EP", f"valid enum value {option!r}", option, True))
        cases.append(Case(name, "EP", f"invalid out-of-enum {OUT_OF_ENUM!r}", OUT_OF_ENUM, False))
    else:
        label = f"valid {typ}" + (f" ({fmt})" if fmt else "")
        cases.append(Case(name, "EP", label, nominal, True))
    cases.append(Case(name, "EP", f"invalid wrong type ({json.dumps(WRONG_TYPE[typ])})", WRONG_TYPE[typ], False))
    if fmt in INVALID_FORMAT:
        cases.append(Case(name, "EP", f"invalid {fmt} format ({INVALID_FORMAT[fmt]!r})", INVALID_FORMAT[fmt], False))
    if not schema.get("nullable", False):
        cases.append(Case(name, "EP", f"invalid null ({'required' if required else 'optional'})", None, False))
    if required:
        cases.append(Case(name, "EP", "invalid missing (required)", MISSING, False))
    else:
        cases.append(Case(name, "EP", "valid omitted (optional)", MISSING, True))
    for value in schema.get("x-invalid-examples", []):
        cases.append(Case(name, "EP", f"invalid example {value!r}", value, False))

    # Length constraints -------------------------------------------------------
    if "maxLength" in schema:
        limit = int(schema["maxLength"])
        cases.append(Case(name, "EP", f"invalid over-max-length ({2 * limit} chars > {limit})", FILL_CHAR * (2 * limit), False))
        for case in bva(name, limit, f"maxLength {limit}", True, below_valid=True, above_valid=False, floor=0):
            case.value = FILL_CHAR * case.value
            cases.append(case)
    if "minLength" in schema:
        limit = int(schema["minLength"])
        for case in bva(name, limit, f"minLength {limit}", True, below_valid=False, above_valid=True, floor=0):
            case.value = FILL_CHAR * case.value
            cases.append(case)

    # Numeric constraints ------------------------------------------------------
    step = 1 if typ == "integer" else schema.get("x-step", 0.01)
    if "minimum" in schema:
        limit = schema["minimum"]
        at = not schema.get("exclusiveMinimum", False)
        cases += bva(name, limit, f"minimum {limit}", at, below_valid=False, above_valid=True, step=step)
    if "maximum" in schema:
        limit = schema["maximum"]
        at = not schema.get("exclusiveMaximum", False)
        cases += bva(name, limit, f"maximum {limit}", at, below_valid=True, above_valid=False, step=step)

    # Cross-field constraint (x-relational) --------------------------------------
    rel = schema.get("x-relational")
    if rel:
        other, op = rel["field"], rel["operator"]
        if other not in base or op not in {">=", ">", "<=", "<"}:
            raise SpecError(f"Field {name}: x-relational needs an operator and a field present in the example")
        limit = base[other]
        below, at, above = {">=": (False, True, True), ">": (False, False, True),
                            "<=": (True, True, False), "<": (True, False, False)}[op]
        if fmt not in {"date", "date-time"} and not isinstance(limit, (int, float)):
            raise SpecError(f"Field {name}: x-relational supports dates and numbers")
        cases += bva(name, limit, f"{name} {op} {other}", at, below_valid=below, above_valid=above,
                     fmt=fmt if fmt in {"date", "date-time"} else None)
    return cases


def path_cases(parameter):
    name = parameter["name"]
    cases = [Case(name, "EP", "valid existing record", MISSING, True, "path")]
    cases += [Case(name, "EP", f"invalid example {v!r}", v, False, "path")
              for v in parameter.get("x-invalid-examples", [])]
    return cases


def auth_cases():
    return [Case("Authorization", "EP", "valid token", "actor", True, "auth"),
            Case("Authorization", "EP", "invalid no token", "none", False, "auth"),
            Case("Authorization", "EP", "invalid unknown token", "invalid", False, "auth")]


def end_after_business_days(start, days):
    """Last day of an interval from start that contains exactly ``days`` weekdays."""
    current, counted = dt.date.fromisoformat(start), 0
    while True:
        counted += current.weekday() < 5
        if counted == days:
            return current.isoformat()
        current += dt.timedelta(days=1)


def rule_cases(rule, fixture):
    """Cases of one x-rule-boundaries entry; the name shown as field is 'a..b'."""
    first, last = rule["fields"]
    name, rid = f"{first}..{last}", rule["rule"]
    cases = []
    if rule["kind"] == "business-days":
        limit = fixture[rule["maximum"]]
        for case in bva(name, limit, f"{rid} business days <= {limit}", True, below_valid=True, above_valid=False):
            case.value = {first: rule["start"], last: end_after_business_days(rule["start"], case.value)}
            cases.append(case)
        end = end_after_business_days(rule["start"], 2 * limit)
        cases.append(Case(name, "EP", f"invalid {rid} {2 * limit} business days", {first: rule["start"], last: end}, False))
    elif rule["kind"] == "interval-overlap":
        interval = fixture[rule["interval"]]
        for limit, label, below, above in ((interval["start"], "existing start", True, False),
                                           (interval["end"], "existing end", False, True)):
            inner = interval["start"] != interval["end"]
            for case in bva(name, limit, f"{rid} {label}", False, below_valid=below or not inner,
                            above_valid=above or not inner, fmt="date"):
                case.value = {first: case.value, last: case.value}
                cases.append(case)
        around = {first: shift(interval["start"], "date", -1), last: shift(interval["end"], "date", 1)}
        cases.append(Case(name, "EP", f"invalid {rid} encloses existing", around, False))
    else:
        raise SpecError(f"Unknown x-rule-boundaries kind {rule['kind']!r}")
    for case in cases:
        case.where = "rule"
    return cases


def request_key(request):
    return json.dumps(request, sort_keys=True, default=lambda v: {"$fixture": v.ref})


class Operation:
    def __init__(self, spec, path, method, op):
        self.path, self.method = path, method
        self.op_id = op.get("operationId") or f"{method}_{path}"
        self.endpoint = f"{method.upper()} {path}"
        schema, example = json_body(spec, op)
        self.schema, self.example = schema, example
        self.success, self.errors = documented_codes(op)
        meta = op.get("x-sqe-test")
        if meta is None:
            raise SpecError(f"{self.endpoint}: x-sqe-test is required for generation")
        self.actor = meta.get("actor")
        if self.actor is not None:
            check_ref(self.actor, f"{self.endpoint} actor")
        self.readback = meta.get("readback")
        if self.readback not in READBACKS:
            raise SpecError(f"{self.endpoint}: readback must be one of {sorted(READBACKS)}")
        self.bindings = {k: check_ref(v, f"{self.endpoint} binding {k}") for k, v in (meta.get("bindings") or {}).items()}
        self.path_params = {k: check_ref(v, f"{self.endpoint} path param {k}") for k, v in (meta.get("path_params") or {}).items()}
        missing_params = set(re.findall(r"{(\w+)}", path)) - set(self.path_params)
        if missing_params:
            raise SpecError(f"{self.endpoint}: no x-sqe-test.path_params for {sorted(missing_params)}")
        self.error_key = meta["error_key"]
        self.invalid_status = {"body": meta["invalid_status"], "rule": meta["invalid_status"], "path": 404, "auth": 401}
        if self.error_key not in {"field", "detail"}:
            raise SpecError(f"{self.endpoint}: error_key must be field or detail")
        props = {k: resolve(spec, v) for k, v in schema.get("properties", {}).items()}
        required = set(schema.get("required", []))
        self.base = {k: Fixture(self.bindings[k]) if k in self.bindings else v for k, v in example.items()}
        self.fields = []
        for name, field_schema in props.items():
            if field_schema.get("readOnly"):
                continue
            self.fields.append((name, field_cases(name, field_schema, name in required, example, self.bindings.get(name))))
        for parameter in op.get("parameters", []):
            if parameter["in"] != "path":
                raise SpecError(f"{self.endpoint}: only path parameters are supported")
            self.fields.append((parameter["name"], path_cases(parameter)))
        rules = {}
        for rule in op.get("x-rule-boundaries", []):
            for case in rule_cases(rule, spec["x-sqe-fixture"]):
                rules.setdefault(case.field, []).append(case)
        self.fields += rules.items()
        if op.get("security", spec.get("security")):
            self.fields.append(("Authorization", auth_cases()))
        self.tests = self.merge()

    def request(self, case):
        request = {"body": dict(self.base), "path": {}, "auth": "actor"}
        if case.where == "auth":
            request["auth"] = case.value
        elif case.where == "path":
            if case.value is not MISSING:
                request["path"] = {case.field: case.value}
        elif case.where == "rule":
            request["body"].update(case.value)
        elif case.value is MISSING:
            request["body"].pop(case.field, None)
        else:
            request["body"][case.field] = case.value
        return request

    def expectation(self, case):
        """(status, error key) of a case."""
        if case.valid:
            return self.success, None
        status = self.invalid_status[case.where]
        if status not in self.errors:
            raise SpecError(f"{self.endpoint}: {status} is not a documented response")
        if case.where == "rule":
            return status, "non_field_errors"
        if case.where == "body":
            return status, case.field if self.error_key == "field" else "detail"
        # A path value that is no integer gets the HTML 404, which has no error key.
        return status, None if case.where == "path" else "detail"

    def merge(self):
        merged, used = {}, set()
        for _, cases in self.fields:
            for case in cases:
                request = self.request(case)
                key = request_key(request)
                expected = self.expectation(case)
                if key in merged:
                    if merged[key]["expected"] != expected:
                        raise SpecError(f"{self.endpoint}: contradictory expectations for {key}")
                    merged[key]["cases"].append(case)
                else:
                    merged[key] = {**request, "expected": expected, "valid": case.valid, "cases": [case],
                                   "name": test_name(case, used)}
        return list(merged.values())


def load_operations(spec):
    ops = []
    for path, item in (spec.get("paths") or {}).items():
        op = item.get("post")
        if op is None:
            continue
        schema, _ = json_body(spec, op)
        if schema is None:
            continue
        ops.append(Operation(spec, path, "post", op))
    if not ops:
        raise SpecError("No POST operation with a JSON request body found")
    return ops


# ---------------------------------------------------------------------------
# Response contract (consumed by tests/team/api/test_openapi_contract.py)
# ---------------------------------------------------------------------------
def deref(spec, node):
    """Copy of node with every local $ref replaced by its target (no recursion support)."""
    node = resolve(spec, node)
    if isinstance(node, dict):
        return {k: deref(spec, v) for k, v in node.items()}
    if isinstance(node, list):
        return [deref(spec, v) for v in node]
    return node


def response_contract(spec, sha):
    operations = {}
    for path, item in spec["paths"].items():
        for method in ("get", "post", "put", "patch", "delete"):
            if method not in item:
                continue
            op = item[method]
            operations[op["operationId"]] = {
                "method": method,
                "path": path,
                "responses": {
                    str(code): {
                        media: deref(spec, content["schema"])
                        for media, content in resolve(spec, response)["content"].items()
                    }
                    for code, response in op["responses"].items()
                },
            }
    return {"generated_by": GENERATOR, "spec_sha256": sha, "operations": operations}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def py(value):
    if value is None or isinstance(value, bool):
        return repr(value)
    if isinstance(value, Fixture):
        return f"F({value.ref!r})"
    if isinstance(value, dict):
        return body_source(value)
    if isinstance(value, str) and len(value) > 40 and set(value) == {FILL_CHAR}:
        return f"{FILL_CHAR!r} * {len(value)}"
    return repr(value)


def body_source(body):
    return "{" + ", ".join(f"{k!r}: {py(v)}" for k, v in body.items()) + "}"


def call_source(test):
    status, error = test["expected"]
    args = [body_source(test["body"]), f"status={status}"]
    if test["path"]:
        args.append(f"path={test['path']!r}")
    if test["auth"] != "actor":
        args.append(f"auth={test['auth']!r}")
    if error:
        args.append(f"error={error!r}")
    return ", ".join(args)


def manifest(ops, sha, source):
    def shown(v):
        if isinstance(v, Fixture):
            return {"fixture": v.ref}
        if isinstance(v, str) and len(v) > 40 and set(v) == {FILL_CHAR}:
            return {"repeat": FILL_CHAR, "length": len(v)}
        return v
    cases = [{
        "test": f"{class_name(op)}.{test['name']}",
        "endpoint": op.endpoint,
        "classes": [f"{c.field} {c.technique} {c.label}" for c in test["cases"]],
        "body": {k: shown(v) for k, v in test["body"].items()},
        "path": test["path"],
        "auth": test["auth"],
        "expected_status": test["expected"][0],
        "expected_error_key": test["expected"][1],
    } for op in ops for test in op.tests]
    return {"generated_by": GENERATOR, "spec_sha256": sha,
            "module_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(), "cases": cases}


def ident(text):
    text = text.replace("''", "empty").replace(" -", " minus ")
    out = re.sub(r"[^0-9a-zA-Z]+", "_", text).strip("_").lower()
    return out or "x"


def test_name(case, used):
    if case.technique == "BVA":
        value, point = case.label.split(" (", 1)
        point = {"limit-1": "below", "limit": "at", "limit+1": "above"}[point.split(",")[0]]
        rule = case.label.split(", ", 1)[1].rstrip(")") if case.where == "rule" else ""
        base = f"test_{ident(case.field)}_bva_{ident(value)}_{point}" + (f"_{ident(rule)}" if rule else "")
    else:
        base = f"test_{ident(case.field)}_ep_{ident(case.label)}"
    base = base[:90].rstrip("_")
    name, n = base, 2
    while name in used or keyword.iskeyword(name):
        name, n = f"{base}_{n}", n + 1
    used.add(name)
    return name


def class_name(op):
    return "Generated" + "".join(part[0].upper() + part[1:] for part in re.split(r"[^0-9a-zA-Z]+", op.op_id) if part) + "Tests"


HARNESS = '''
class F:
    """Fixture-bound value (x-sqe-test binding), resolved inside the test."""

    def __init__(self, ref):
        self.ref = ref


class GeneratedApiTestCase(TestCase):
    """Runtime harness emitted by the generator; uses the A2.1 fixtures and token clients."""

    METHOD = PATH = READBACK = None
    ACTOR = None
    PATH_PARAMS = {}
    SUCCESS = 200

    def setUp(self):
        # x-sqe-fixture: every allowance, and the W2 target / overlap interval, a
        # pending team A request of e1 that m1 may decide.
        self.people = build_people("gen", allowance=FIXTURE["allowance"])
        self.pending = make_request(
            self.people.e1, start=date.fromisoformat(FIXTURE["pending"]["start"]),
            end=date.fromisoformat(FIXTURE["pending"]["end"]),
        )

    def ref(self, ref):
        root, *attrs = ref.split(".")
        value = {"pending": self.pending, "password": TEST_PASSWORD}.get(root)
        if value is None:
            value = getattr(self.people, root)
        for attr in attrs:
            value = getattr(value, attr)
        return value

    def resolve(self, body):
        return {k: self.ref(v.ref) if isinstance(v, F) else v for k, v in body.items()}

    def url(self, path):
        return self.PATH.format(**{**{k: self.ref(v) for k, v in self.PATH_PARAMS.items()}, **path})

    def client_for(self, auth):
        if auth == "actor" and self.ACTOR:
            return token_client(self.ref(self.ACTOR))
        client = APIClient()
        if auth == "invalid":
            client.credentials(HTTP_AUTHORIZATION="Token " + "0" * 40)
        return client

    def snapshot(self):
        if self.READBACK == "created":
            return LeaveRequest.objects.filter(employee=self.ref(self.ACTOR)).count()
        if self.READBACK == "decided":
            return LeaveRequest.objects.filter(pk=self.pending.pk).values("status", "decided_by_id").get()
        return Token.objects.count()

    def check(self, body, *, status, path=None, auth="actor", error=None):
        """One real API call with one generated request; assert status, error key and persisted outcome."""
        client = self.client_for(auth)
        body = self.resolve(body)
        before = self.snapshot()
        response = getattr(client, self.METHOD)(self.url(path or {}), body, format="json")
        data = getattr(response, "data", None)
        shown = "(login body hidden)" if self.READBACK == "token" else repr(data)
        detail = f"{self.METHOD.upper()} {self.PATH} -> {response.status_code}, expected {status}: {shown}"
        self.assertEqual(response.status_code, status, detail)
        valid = status == self.SUCCESS
        if error is not None:
            self.assertEqual(set(data), {error}, detail)
        after = self.snapshot()
        if self.READBACK == "created":
            self.assertEqual(after - before, 1 if valid else 0, "LeaveRequest rows created")
        elif self.READBACK == "decided":
            expected = {"status": body["status"], "decided_by_id": self.ref(self.ACTOR).pk} if valid else before
            self.assertEqual(after, expected, "decision persisted state")
        else:
            self.assertEqual("token" in data, valid, "token in response")
            self.assertEqual(after - before, 1 if valid else 0, "tokens created")
        return response
'''


def render(spec_path, spec_text, ops, demo_env, command, fixture):
    sha = hashlib.sha256(spec_text.encode("utf-8")).hexdigest()
    total = sum(len(op.tests) for op in ops)
    lines = [
        "# =============================================================================",
        "# GENERATED FILE - DO NOT EDIT BY HAND.",
        f"# Generator: {GENERATOR}",
        f"# Spec:      {spec_path}",
        f"# Spec SHA-256: {sha}",
        f"# Command:   {command}",
        "#",
        "# Test design (from the spec's constraints, one input varied per test, all",
        "# other inputs at the operation's example values):",
        "#   EP  valid: each enum value / the declared type / omitted optional field;",
        "#       invalid: wrong type, out-of-enum, invalid format, null, missing required",
        "#       field, over-max-length, x-invalid-examples, missing/unknown token.",
        "#   BVA 3-point (limit-1, limit, limit+1) for maxLength/minLength/minimum/",
        "#       maximum, x-relational and x-rule-boundaries constraints.",
        "# Identical requests are generated once; the docstring lists every",
        "# class the test covers (count each executable case once).",
        f"# Tests: {total}",
    ]
    if demo_env:
        name, value = demo_env
        lines += [
            "#",
            f"# DEMONSTRATION MODULE: its tests load only when {name}={value}.",
            "# It encodes a changed spec and is expected to fail against the unchanged",
            "# application; normal discovery of tests.team loads no tests from it.",
        ]
    lines += [
        "# =============================================================================",
        '"""OpenAPI-generated EP/BVA API tests (A2.4). Regenerate instead of editing."""',
        "",
    ]
    if demo_env:
        lines += ["import os"]
    lines += [
        "from datetime import date",
        "",
        "from django.test import TestCase",
        "from rest_framework.authtoken.models import Token",
        "from rest_framework.test import APIClient",
        "",
        "from leave.models import LeaveRequest",
        "from tests.team.api.support import token_client",
        "from tests.team.fixtures.leave_data import TEST_PASSWORD, build_people, make_request",
        "",
        f"SPEC_SHA256 = {sha!r}",
        f"FIXTURE = {fixture!r}",
    ]
    if demo_env:
        name, value = demo_env
        lines += [
            f"DEMO_ENABLED = os.environ.get({name!r}) == {value!r}",
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
            f"    METHOD = {op.method!r}",
            f"    PATH = {op.path!r}",
            f"    ACTOR = {op.actor!r}",
            f"    PATH_PARAMS = {op.path_params!r}",
            f"    READBACK = {op.readback!r}",
            f"    SUCCESS = {op.success!r}",
        ]
        for test in op.tests:
            first, *others = test["cases"]
            lines += ["", f"    def {test['name']}(self):"]
            doc = [f"Generated from spec: {op.endpoint} {first.field} {first.technique} {first.label}"]
            if others:
                doc += [""] + [f"Also generated from spec: {op.endpoint} {c.field} {c.technique} {c.label}" for c in others]
            status, error = test["expected"]
            doc += ["", f"Expect {status}" + (f", error key {error}." if error else ".")]
            lines.append('        """' + doc[0])
            lines += [("        " + d if d else "") for d in doc[1:]]
            lines.append('        """')
            lines.append(f"        self.check({call_source(test)})")
    return "\n".join(lines) + "\n"


def summary(ops):
    out = []
    for op in ops:
        out.append(f"Endpoint: {op.endpoint}")
        for name, cases in op.fields:
            ep_valid = sum(1 for c in cases if c.technique == "EP" and c.valid)
            ep_invalid = sum(1 for c in cases if c.technique == "EP" and not c.valid)
            out.append(f"{name}: {ep_valid} valid EP, {ep_invalid} invalid EP")
            bva_cases = [c for c in cases if c.technique == "BVA"]
            if bva_cases:
                shown = ", ".join(c.label.split(" (")[0] for c in bva_cases)
                out.append(f"{name}: {len(bva_cases)} BVA values ({shown})")
        cases = sum(len(c) for _, c in op.fields)
        out.append(f"-> {cases} cases, {len(op.tests)} tests after merging identical requests")
        out.append("")
    total = sum(len(op.tests) for op in ops)
    out.append(f"Total: {total} tests generated")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("spec", nargs="?", default=DEFAULT_SPEC, help="OpenAPI YAML path (relative to the repo root or absolute)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="generated test module path")
    parser.add_argument("--demo-env", metavar="NAME=VALUE", help="load the generated tests only when NAME=VALUE")
    args = parser.parse_args(argv)

    spec_path = Path(args.spec)
    spec_file = spec_path if spec_path.is_absolute() else ROOT / spec_path
    out_path = Path(args.output)
    out_file = out_path if out_path.is_absolute() else ROOT / out_path
    demo_env = None
    if args.demo_env:
        name, sep, value = args.demo_env.partition("=")
        if not sep or not re.fullmatch(r"[A-Z][A-Z0-9_]*", name) or not value:
            parser.error("--demo-env must look like NAME=VALUE")
        demo_env = (name, value)

    spec_text = spec_file.read_text(encoding="utf-8")
    spec = yaml.safe_load(spec_text)
    if not str(spec.get("openapi", "")).startswith("3.0"):
        parser.error("Only OpenAPI 3.0 documents are supported")
    try:
        ops = load_operations(spec)
    except (SpecError, KeyError, TypeError, ValueError) as exc:
        sys.exit(f"Spec error: {exc!r}")

    command = " ".join(["python3", GENERATOR, str(args.spec), "--output", str(args.output)]
                       + (["--demo-env", args.demo_env] if args.demo_env else []))
    source = render(args.spec, spec_text, ops, demo_env, command, spec["x-sqe-fixture"])
    compile(source, str(out_file), "exec")  # fail before writing if the output is not valid Python

    out_file.parent.mkdir(parents=True, exist_ok=True)
    init = out_file.parent / "__init__.py"
    if not init.exists():
        init.write_text('"""Generated API tests."""\n', encoding="utf-8")
    out_file.write_text(source, encoding="utf-8")
    if not demo_env:
        sha = hashlib.sha256(spec_text.encode("utf-8")).hexdigest()
        contract = json.dumps(response_contract(spec, sha), indent=1, sort_keys=True, ensure_ascii=False)
        (out_file.parent / CONTRACT_NAME).write_text(contract + "\n", encoding="utf-8")
        cases = json.dumps(manifest(ops, sha, source), indent=1, ensure_ascii=False)
        (out_file.parent / MANIFEST_NAME).write_text(cases + "\n", encoding="utf-8")
    print(summary(ops))
    print(f"Written: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
