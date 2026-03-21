#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

if [ -f "$root_dir/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$root_dir/.env"
  set +a
fi

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-sima_dance}"
POSTGRES_PORT="${POSTGRES_PORT:-5433}"

export DATABASE_URL="${DATABASE_URL:-postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}}"
export SECRET_KEY="${DJANGO_SECRET_KEY:-change_me}"
export DEBUG="${DJANGO_DEBUG:-True}"

backend_python="$root_dir/backend/.venv/bin/python"
if [ ! -x "$backend_python" ]; then
  backend_python="python"
fi

run_smoke=false
test_targets=()

for arg in "$@"; do
  if [ "$arg" = "--smoke" ]; then
    run_smoke=true
  else
    test_targets+=("$arg")
  fi
done

if [ "${#test_targets[@]}" -eq 0 ]; then
  test_targets=(accounts booking)
fi

echo "Running Django tests: ${test_targets[*]}"
(
  cd "$root_dir/backend"
  "$backend_python" manage.py test "${test_targets[@]}"
)

if [ "$run_smoke" = true ]; then
  echo "Running local smoke checks..."
  "$root_dir/scripts/tests/smoke_local.sh"
fi
