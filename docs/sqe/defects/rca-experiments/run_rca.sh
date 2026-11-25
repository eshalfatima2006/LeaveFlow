#!/usr/bin/env bash
# RCA experiments for the two major defects. Usage: run_rca.sh NEW_OUTPUT_DIR
# Every variant runs in a throwaway clone under /tmp and on a throwaway PostgreSQL
# container; the working tree and the development database are never touched.
# The variants are experiments that test a cause. They are NOT the product fix.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(git -C "$HERE" rev-parse --show-toplevel); PY=$ROOT/.venv/bin/python
OUT=$1; mkdir "$OUT"; OUT=$(cd "$OUT" && pwd)
clone() { D=$(mktemp -d /tmp/rca-XXXXXX); git clone -q --no-hardlinks "$ROOT" "$D/r"; }
{ echo "commit $(git -C "$ROOT" rev-parse HEAD)"; "$PY" -V; "$PY" -m pip list 2>/dev/null | grep -iE '^(django|djangorestframework|gunicorn|psycopg) '
  sha256sum "$ROOT/tests/team/fixtures/leave_data.py" "$ROOT/docs/sqe/openapi/leaveflow-api.yaml" | sed "s#$ROOT/##"; date -u +%FT%TZ; } > "$OUT/environment.txt"
for v in baseline w1-atomic-only w1-lock-overlapping-rows w1-lock-employee-row w1-serializable w1-exclusion-constraint w2-check-only w2-check-and-lock-balance; do
  clone; cd "$D/r"
  rm tests/team/concurrency/test_concurrency.py; cp "$HERE/rca_observe.py" tests/team/concurrency/test_rca.py
  python3 "$HERE/variants.py" "$D/r" $v
  git add -A backend; git diff --cached -- backend > "$OUT/$v.diff"; [ -s "$OUT/$v.diff" ] || rm "$OUT/$v.diff"
  RCA_VARIANT=$v "$PY" scripts/sqe/run_concurrency.py > "$OUT/$v.log" 2>&1 || true
  grep -hoE 'RCA \{.*|concurrency: exit.*' "$OUT/$v.log" | tee -a "$OUT/results.txt"
  cd /; rm -rf "$D"
done
for v in w1-lock-employee-row w2-check-and-lock-balance; do  # impact: which existing tests notice the change
  clone; cd "$D/r"; python3 "$HERE/variants.py" "$D/r" $v
  for s in upstream team; do
    "$PY" scripts/sqe/run_tests.py $s > "$OUT/impact-$v-$s.log" 2>&1 || true
    { echo "== $v: $s suite"; grep -hE '^(Ran |OK|FAILED|FAIL:|ERROR:)' "$OUT/impact-$v-$s.log"; } | tee -a "$OUT/impact.txt"
  done
  cd /; rm -rf "$D"; rm -f "$OUT"/impact-$v-*.log
done
clone; "$PY" "$HERE/http_race.py" "$D/r" "$ROOT/.venv" | tee "$OUT/http.txt"; rm -rf "$D"