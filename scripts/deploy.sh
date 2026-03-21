#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

env_file="$root_dir/.env.production"
build_flag="--build"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/deploy.sh [options]

Options:
  --env-file PATH   Env file for docker compose. Default: .env.production
  --no-build        Skip image rebuild before start.
  --help            Show this help.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --env-file)
      env_file="${2:-}"
      shift 2
      ;;
    --no-build)
      build_flag=""
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required to deploy the stack." >&2
  exit 1
fi

if [ ! -f "$env_file" ]; then
  echo "Env file not found: $env_file" >&2
  echo "Generate it first with ./scripts/generate_prod_env.sh" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$env_file"
set +a

required_vars=(
  TRAEFIK_ACME_EMAIL
  TRAEFIK_WEB_HOST
  TRAEFIK_API_HOST
  POSTGRES_PASSWORD
  DJANGO_SECRET_KEY
)

for var_name in "${required_vars[@]}"; do
  if [ -z "${!var_name:-}" ]; then
    echo "Required variable is empty in $env_file: $var_name" >&2
    exit 1
  fi
done

compose_cmd=(docker compose --env-file "$env_file" -f "$root_dir/docker-compose.yml")
services=(traefik postgres backend frontend)

echo "Deploying stack with $env_file"
"${compose_cmd[@]}" up -d ${build_flag:+$build_flag} --remove-orphans "${services[@]}"

wait_for_service() {
  local service="$1"
  local expected_state="$2"
  local retries="${3:-60}"

  local container_id=""
  container_id="$("${compose_cmd[@]}" ps -q "$service" || true)"
  if [ -z "$container_id" ]; then
    echo "Could not find container for service: $service" >&2
    return 1
  fi

  echo "Waiting for ${service} to reach state ${expected_state}..."
  for _ in $(seq 1 "$retries"); do
    state="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id" 2>/dev/null || true)"
    if [ "$state" = "$expected_state" ]; then
      echo "${service} is ${expected_state}."
      return 0
    fi
    sleep 2
  done

  echo "Timed out waiting for ${service}. Current state: ${state:-unknown}" >&2
  return 1
}

wait_for_http() {
  local url="$1"
  local host="$2"
  local name="$3"

  if ! command -v curl >/dev/null 2>&1; then
    echo "curl is not installed; skipping HTTP readiness check for ${name}."
    return 0
  fi

  echo "Waiting for ${name} at ${url}..."
  for _ in $(seq 1 60); do
    status="$(curl -k -s -o /dev/null -w '%{http_code}' --resolve "${host}:443:127.0.0.1" "$url" || true)"
    if [ "$status" != "000" ]; then
      echo "${name} responded with HTTP ${status}."
      return 0
    fi
    sleep 2
  done

  echo "Timed out waiting for ${name} at ${url}." >&2
  return 1
}

wait_for_service "postgres" "healthy" 60
wait_for_service "backend" "running" 60
wait_for_service "frontend" "running" 60
wait_for_service "traefik" "running" 60

wait_for_http "https://${TRAEFIK_API_HOST}/api/" "$TRAEFIK_API_HOST" "backend"
wait_for_http "https://${TRAEFIK_WEB_HOST}/" "$TRAEFIK_WEB_HOST" "frontend"

echo
echo "Deploy finished."
echo "Frontend: https://${TRAEFIK_WEB_HOST}"
echo "Backend:  https://${TRAEFIK_API_HOST}/api/"
echo
echo "Current services:"
"${compose_cmd[@]}" ps
