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

if [ "$skip_superuser" != true ]; then
  bash "$root_dir/scripts/ensure_superuser_docker.sh" --env-file "$env_file"
fi

echo "Installing initial booking data..."
bash "$root_dir/scripts/install_data.sh" \
  --api-base "https://${TRAEFIK_API_HOST}/api/booking" \
  --insecure \
  --event-create-mode if-empty \
  "${set_prices_args[@]}"

echo "Ensuring signup groups exist..."
bash "$root_dir/scripts/set_groups.sh" --docker --env-file "$env_file" --skip-migrate
