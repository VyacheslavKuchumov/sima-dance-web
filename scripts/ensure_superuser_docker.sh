#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

env_file="$root_dir/.env.production"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/ensure_superuser_docker.sh [options]

Options:
  --env-file PATH   Env file for docker compose. Default: .env.production
  --help            Show this help.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --env-file)
      env_file="${2:-}"
      shift 2
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

if [ ! -f "$env_file" ]; then
  echo "Env file not found: $env_file" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$env_file"
set +a

required_superuser_vars=(
  DJANGO_SUPERUSER_USERNAME
  DJANGO_SUPERUSER_EMAIL
  DJANGO_SUPERUSER_PASSWORD
)

for var_name in "${required_superuser_vars[@]}"; do
  if [ -z "${!var_name:-}" ]; then
    echo "Required superuser variable is empty in $env_file: $var_name" >&2
    exit 1
  fi
done

compose_cmd=(docker compose --env-file "$env_file" -f "$root_dir/docker-compose.yml")

echo "Ensuring Django superuser exists..."
"${compose_cmd[@]}" exec -T \
  -e DJANGO_SUPERUSER_USERNAME="$DJANGO_SUPERUSER_USERNAME" \
  -e DJANGO_SUPERUSER_EMAIL="$DJANGO_SUPERUSER_EMAIL" \
  -e DJANGO_SUPERUSER_PASSWORD="$DJANGO_SUPERUSER_PASSWORD" \
  backend python manage.py shell -c "
from django.contrib.auth import get_user_model
from django.db import transaction
import os

User = get_user_model()
username = os.environ['DJANGO_SUPERUSER_USERNAME']
email = os.environ['DJANGO_SUPERUSER_EMAIL']
password = os.environ['DJANGO_SUPERUSER_PASSWORD']

with transaction.atomic():
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    print('Created superuser' if created else 'Updated superuser')
"
