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

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required to start the stack. Please install Docker first."
  exit 1
fi

compose_files=(-f "$root_dir/docker-compose.yml" -f "$root_dir/docker-compose.local.yml")
services=(postgres backend frontend)

docker compose "${compose_files[@]}" up -d --build "${services[@]}"

pg_container_id="$(docker compose "${compose_files[@]}" ps -q postgres || true)"
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

wait_for_http "http://localhost:8000/api/" "backend"
wait_for_http "http://localhost:3000/" "frontend"

echo "Docker stack is running."
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
