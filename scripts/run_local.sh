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

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-sima_dance}"
POSTGRES_PORT="${POSTGRES_PORT:-5433}"

DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required to start the database. Please install Docker first."
  exit 1
fi

docker compose up -d postgres

pg_container_id="$(docker compose ps -q postgres || true)"
if [ -n "$pg_container_id" ]; then
  echo "Waiting for postgres to become healthy..."
  for _ in {1..30}; do
    status="$(docker inspect -f '{{.State.Health.Status}}' "$pg_container_id" 2>/dev/null || true)"
    if [ "$status" = "healthy" ]; then
      echo "Postgres is healthy."
      break
    fi
    sleep 1
  done
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
