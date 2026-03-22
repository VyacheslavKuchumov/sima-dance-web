#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

env_file="$root_dir/.env.production"
no_build=false
skip_superuser=false
set_prices_args=()

usage() {
  cat <<'EOF'
Usage:
  ./scripts/init_deploy.sh [options] [install_data options]

Options:
  --env-file PATH   Env file for docker compose. Default: .env.production
  --no-build        Skip image rebuild before start.
  --skip-superuser  Skip automatic superuser creation/update.
  --help            Show this help.

Any additional options are passed to scripts/install_data.sh.
Examples:
  ./scripts/init_deploy.sh
  ./scripts/init_deploy.sh --event-title "Концерт" --event-date 2026-04-01
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --env-file)
      env_file="${2:-}"
      shift 2
      ;;
    --no-build)
      no_build=true
      shift
      ;;
    --skip-superuser)
      skip_superuser=true
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      set_prices_args+=("$1")
      shift
      ;;
  esac
done

deploy_args=(--env-file "$env_file" --skip-set-prices)
if [ "$no_build" = true ]; then
  deploy_args+=(--no-build)
fi

echo "Running initial deploy..."
bash "$root_dir/scripts/deploy.sh" "${deploy_args[@]}"

set -a
# shellcheck disable=SC1090
source "$env_file"
set +a

compose_cmd=(docker compose --env-file "$env_file" -f "$root_dir/docker-compose.yml")

echo "Installing initial booking data..."
bash "$root_dir/scripts/install_data.sh" \
  --api-base "https://${TRAEFIK_API_HOST}/api/booking" \
  --event-create-mode if-empty \
  "${set_prices_args[@]}"

if [ "$skip_superuser" != true ]; then
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
fi
