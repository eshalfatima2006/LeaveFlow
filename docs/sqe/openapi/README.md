# OpenAPI contract and generated tests

| File | Purpose |
|---|---|
| [leaveflow-api.yaml](leaveflow-api.yaml) | Baseline spec; its header explains each `x-` extension |
| `changes/*.patch` | The exact constraint changes of [CHANGE-1](CHANGE-1-NOTE-LENGTH.md), [CHANGE-2](CHANGE-2-SICK-TYPE.md) and [CHANGE-3](CHANGE-3-NULLABLE-NOTE.md) |
| `scripts/sqe/generate_api_tests.py` | Generator |
| `tests/team/generated/test_generated_api.py` | Baseline tests (the only ones the default suite runs) |
| `tests/team/generated/generated_cases.json` | Case manifest, with reasons where a technique does not apply |
| `tests/team/generated/api_contract.json` | Resolved spec used by the contract tests and the coverage tool |

## Fresh checkout

Measured with Python 3.12.7, Django 6.0.7, DRF 3.17.1, PyYAML 6.0.3, GNU patch, Docker with PostgreSQL 17.12 (concurrency only). PyYAML is needed by the generator only, never by the application or the tests.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r scripts/sqe/requirements-generator.txt
.venv/bin/python scripts/sqe/generate_api_tests.py            # must leave `git status` clean
.venv/bin/python scripts/sqe/run_tests.py team                # in-memory database
.venv/bin/python scripts/sqe/api_coverage.py --evidence-dir /tmp/api-coverage   # must be a new directory
.venv/bin/python scripts/sqe/run_concurrency.py               # throwaway PostgreSQL container
```

`test_generated_manifest.py` and `test_openapi_contract.py` fail when the spec, the generated module, the manifest and the exported contract do not belong together, so a changed spec without regeneration is detected. Never edit a generated file.

## Constraint changes

`--patch` applies the change in memory; the baseline spec is never edited. Example (change 1 → v2):

```bash
.venv/bin/python scripts/sqe/generate_api_tests.py --patch docs/sqe/openapi/changes/change-1-note-length.patch \
    --output tests/team/generated/test_generated_api_v2.py --demo-env SQE_SPEC_CHANGE_DEMO=v2
SQE_SPEC_CHANGE_DEMO=v2 .venv/bin/python scripts/sqe/run_tests.py team tests.team.generated.test_generated_api_v2
```

| Change | Module | Changed spec SHA-256 | Generated | Expected failures against the unchanged app |
|---|---|---|---|---|
| 1 `note` limit 280 → 200 | v2 | `426adf51…81e2` | 127 | 2: 201 characters, and 201 characters padded with spaces (app 201, spec 400) |
| 2 `leave_type` adds `sick` | v3 | `3f898cac…473e` | 128 | 1: `sick` (app 400, spec 201) |
| 3 `note` nullable | v4 | `cbfc8d9c…bf09` | 127 | 1: null (app 400, spec 201) |

Baseline spec SHA-256 `939d1303b296138c872a55f84823eeb15d0370925cc840fe5f14c6064fcd0b41` (27 Nov 2026: operation-flow conditions added; the constraint changes and their predicted failures are unchanged, the hashes in the CHANGE documents are those of their original runs); 127 tests, all passing. In a viva, edit the spec directly, regenerate without `--patch`, and predict which tests change.

## CI (not changed here)

`.github/workflows/ci.yml` runs only the upstream Django tests. It is owned by Member 1 (A1), so the job below is a proposal, not a change:

```yaml
  team-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with: { python-version: '3.12' }
      - run: pip install -r requirements.txt -r scripts/sqe/requirements-generator.txt
      - run: python scripts/sqe/generate_api_tests.py && git diff --exit-code
      - run: python scripts/sqe/run_tests.py team --evidence-dir team-results
      - if: always()
        uses: actions/upload-artifact@v4
        with: { name: team-results, path: team-results }
```
