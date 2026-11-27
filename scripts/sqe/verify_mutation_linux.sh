#!/usr/bin/env bash
# Use Linux-native files for fork-based mutmut, especially when invoked from WSL.
set -euo pipefail
repo=$(cd "${1:-$(dirname "$0")/../..}" && pwd)
run_dir=$(mktemp -d /tmp/leaveflow-mutation-XXXXXX)
printf 'Linux mutation workspace: %s\n' "$run_dir"
tar -C "$repo" --exclude=.git --exclude=.venv-linux --exclude=mutants --exclude=.pytest_cache --exclude=api-results --exclude='__pycache__' -cf - . | tar -C "$run_dir" -xf -
python3 -m venv "$run_dir/.venv"
"$run_dir/.venv/bin/pip" install -q -r "$run_dir/requirements.txt" -r "$run_dir/requirements-sqe.txt"
"$run_dir/.venv/bin/python" --version > "$run_dir/mutation-environment.txt"
"$run_dir/.venv/bin/pip" freeze >> "$run_dir/mutation-environment.txt"
cd "$run_dir"
set +e
"$run_dir/.venv/bin/python" scripts/sqe/mutmut_custom.py run --max-children 4 > mutmut-run.log 2>&1
mutation_exit=$?
set -e
cp mutmut-run.log "$repo/mutmut-run.log"
cp mutation-environment.txt "$repo/mutation-environment.txt"
if [ -d mutants ]; then cp -R mutants "$repo/"; fi
printf 'Mutation runner exit: %s; workspace retained at %s\n' "$mutation_exit" "$run_dir"
exit "$mutation_exit"
