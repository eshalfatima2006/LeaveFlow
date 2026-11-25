"""Strict response validation against the exported OpenAPI contract (standard library only).

``tests/team/generated/api_contract.json`` is written by
``scripts/sqe/generate_api_tests.py`` from ``docs/sqe/openapi/leaveflow-api.yaml``.
Only the schema keywords the spec uses are implemented; an unknown keyword raises,
so a constraint is never skipped silently. Properties that the schema does not
document are reported, which is stricter than OpenAPI's default.
"""

from datetime import date, datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC_PATH = ROOT / "docs/sqe/openapi/leaveflow-api.yaml"
CONTRACT = json.loads((ROOT / "tests/team/generated/api_contract.json").read_text(encoding="utf-8"))

ANNOTATIONS = {"description", "default", "example", "title"}
KEYWORDS = {
    "type", "format", "enum", "nullable", "required", "properties", "additionalProperties",
    "items", "maxItems", "maxLength", "minimum", "oneOf", "allOf",
}
TYPES = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
FORMATS = {"date": date.fromisoformat, "date-time": datetime.fromisoformat}


def merge_all_of(schema):
    """One object schema out of an allOf list, so undocumented properties stay detectable."""
    merged = {"type": "object", "properties": {}, "required": []}
    for part in schema["allOf"]:
        part = merge_all_of(part) if "allOf" in part else part
        if set(part) - ANNOTATIONS - {"type", "properties", "required"}:
            raise NotImplementedError("allOf supports plain object schemas only")
        merged["properties"].update(part.get("properties", {}))
        merged["required"] += part.get("required", [])
    return merged


def errors(value, schema, where="$"):
    """List of contract violations; empty when ``value`` conforms."""
    unknown = {k for k in schema if not k.startswith("x-")} - KEYWORDS - ANNOTATIONS
    if unknown:
        raise NotImplementedError(f"{where}: unsupported schema keywords {sorted(unknown)}")
    if "allOf" in schema:
        return errors(value, merge_all_of(schema), where)
    if "oneOf" in schema:
        matches = [s for s in schema["oneOf"] if not errors(value, s, where)]
        return [] if len(matches) == 1 else [f"{where}: matches {len(matches)} oneOf schemas, expected 1"]
    if value is None:
        return [] if schema.get("nullable") else [f"{where}: null is not allowed"]
    kind = schema["type"]
    if not isinstance(value, TYPES[kind]) or (kind == "integer" and isinstance(value, bool)):
        return [f"{where}: expected {kind}, got {type(value).__name__}"]
    found = []
    if "enum" in schema and value not in schema["enum"]:
        found.append(f"{where}: {value!r} not in enum")
    if "maxLength" in schema and len(value) > schema["maxLength"]:
        found.append(f"{where}: longer than {schema['maxLength']}")
    if "minimum" in schema and value < schema["minimum"]:
        found.append(f"{where}: below {schema['minimum']}")
    if schema.get("format") in FORMATS:
        try:
            FORMATS[schema["format"]](value)
        except ValueError:
            found.append(f"{where}: not a {schema['format']}")
    elif "format" in schema and schema["format"] != "password":
        raise NotImplementedError(f"{where}: unsupported format {schema['format']}")
    if kind == "array":
        if len(value) > schema.get("maxItems", len(value)):
            found.append(f"{where}: more than {schema['maxItems']} items")
        for n, item in enumerate(value):
            found += errors(item, schema["items"], f"{where}[{n}]")
    if kind == "object":
        properties = schema.get("properties", {})
        found += [f"{where}.{k}: missing" for k in schema.get("required", []) if k not in value]
        for key, item in value.items():
            if key in properties:
                found += errors(item, properties[key], f"{where}.{key}")
            elif "additionalProperties" in schema:
                found += errors(item, schema["additionalProperties"], f"{where}.{key}")
            else:
                found.append(f"{where}.{key}: undocumented property")
    return found


def response_errors(operation_id, response):
    """Violations of status, media type and body for one real response."""
    operation = CONTRACT["operations"][operation_id]
    documented = operation["responses"].get(str(response.status_code))
    if documented is None:
        return [f"{operation_id}: undocumented status {response.status_code}"]
    media = response.get("Content-Type", "").split(";")[0]
    if media not in documented:
        return [f"{operation_id} {response.status_code}: undocumented media type {media!r}"]
    value = response.json() if media == "application/json" else response.content.decode()
    return errors(value, documented[media], f"{operation_id} {response.status_code}")
