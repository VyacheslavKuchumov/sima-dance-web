#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

env_file="$root_dir/.env.production"
use_docker=false
skip_migrate=false

usage() {
  cat <<'EOF'
Usage:
  ./scripts/set_groups.sh [options]

Options:
  --docker          Run inside the backend Docker container.
  --env-file PATH   Env file for docker compose in --docker mode. Default: .env.production
  --skip-migrate    Skip automatic migrate before syncing groups.
  --help            Show this help.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --docker)
      use_docker=true
      shift
      ;;
    --env-file)
      env_file="${2:-}"
      shift 2
      ;;
    --skip-migrate)
      skip_migrate=true
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

if [ "$use_docker" = true ]; then
  if [ ! -f "$env_file" ]; then
    echo "Env file not found: $env_file" >&2
    exit 1
  fi

  compose_cmd=(docker compose --env-file "$env_file" -f "$root_dir/docker-compose.yml")

  if [ "$skip_migrate" != true ]; then
    echo "Applying migrations in Docker before syncing signup groups..."
    "${compose_cmd[@]}" exec -T backend python manage.py migrate
  fi

  echo "Syncing signup groups in Docker..."
  "${compose_cmd[@]}" exec -T backend python manage.py set_groups
  exit 0
fi

if [ -f "$root_dir/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$root_dir/.env"
  set +a
fi

export DATABASE_URL="${DATABASE_URL:-sqlite:///$root_dir/backend/db.sqlite3}"
export SECRET_KEY="${SECRET_KEY:-${DJANGO_SECRET_KEY:-change_me}}"
export DEBUG="${DEBUG:-${DJANGO_DEBUG:-True}}"

backend_python="$root_dir/backend/.venv/bin/python"
if [ ! -x "$backend_python" ]; then
  if command -v python3 >/dev/null 2>&1; then
    backend_python="python3"
  else
    backend_python="python"
  fi
fi

echo "Syncing signup groups locally..."
(
  cd "$root_dir/backend"
  if [ "$skip_migrate" != true ]; then
    echo "Applying migrations before syncing signup groups..."
    "$backend_python" manage.py migrate
  fi
  "$backend_python" manage.py set_groups
)
