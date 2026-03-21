#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

if [ ! -f "$root_dir/.env" ]; then
  cp "$root_dir/.env.example" "$root_dir/.env"
  echo "Created .env from .env.example. Please update POSTGRES_PASSWORD and DJANGO_SECRET_KEY."
fi

set -a
# shellcheck disable=SC1091
source "$root_dir/.env"
set +a

wait_for_http() {
  local url="$1"
  local name="$2"

  if ! command -v curl >/dev/null 2>&1; then
    echo "curl is not installed; skipping HTTP readiness check for ${name}."
    return 0
  fi

  echo "Waiting for ${name} at ${url}..."
  for _ in {1..60}; do
    status="$(curl -s -o /dev/null -w "%{http_code}" "$url" || true)"
    if [ "$status" != "000" ]; then
      echo "${name} responded with HTTP ${status}."
      return 0
    fi
    sleep 1
  done

  echo "Timed out waiting for ${name}."
  return 1
}

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-sima_dance}"
POSTGRES_PORT="${POSTGRES_PORT:-5433}"

DATABASE_URL="${DATABASE_URL:-postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}}"

if ! command -v python >/dev/null 2>&1; then
  echo "Python is required to start the backend."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to start the frontend."
  exit 1
fi

if command -v pg_isready >/dev/null 2>&1; then
  echo "Checking local postgres availability..."
  if ! pg_isready -h 127.0.0.1 -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; then
    echo "Postgres is not available at 127.0.0.1:${POSTGRES_PORT}."
    echo "Please start a local Postgres or set DATABASE_URL."
    exit 1
  fi
else
  echo "pg_isready not found; skipping postgres availability check."
fi

backend_python="$root_dir/backend/.venv/bin/python"
if [ ! -x "$backend_python" ]; then
  backend_python="python"
fi

cleanup() {
  echo "Stopping dev servers..."
  kill "${backend_pid:-}" "${frontend_pid:-}" 2>/dev/null || true
}
trap cleanup INT TERM

(
  cd "$root_dir/backend"
  export DATABASE_URL
  export SECRET_KEY="${DJANGO_SECRET_KEY:-change_me}"
  export DEBUG="${DJANGO_DEBUG:-True}"
  "$backend_python" manage.py migrate
  "$backend_python" manage.py runserver
) &
backend_pid=$!

echo "Backend started (PID $backend_pid)."

(
  cd "$root_dir/frontend"
  export NUXT_DEVTOOLS="${NUXT_DEVTOOLS:-false}"
  npm run dev
) &
frontend_pid=$!

echo "Frontend started (PID $frontend_pid)."

wait_for_http "http://localhost:8000/api/" "backend"
wait_for_http "http://localhost:3000/" "frontend"

if [ -x "$root_dir/scripts/tests/smoke_local.sh" ]; then
  "$root_dir/scripts/tests/smoke_local.sh"
else
  echo "Smoke test script not found; skipping tests."
fi

echo "Local stack is running."
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"

while true; do
  if ! kill -0 "$backend_pid" 2>/dev/null; then
    echo "Backend process exited."
    break
  fi
  if ! kill -0 "$frontend_pid" 2>/dev/null; then
    echo "Frontend process exited."
    break
  fi
  sleep 1
done

cleanup
wait || true
