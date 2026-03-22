#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

env_file="$root_dir/.env.production"
no_build=false
set_prices_args=()

usage() {
  cat <<'EOF'
Usage:
  ./scripts/init_deploy.sh [options] [install_data options]

Options:
  --env-file PATH   Env file for docker compose. Default: .env.production
  --no-build        Skip image rebuild before start.
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

echo "Installing initial booking data..."
bash "$root_dir/scripts/install_data.sh" \
  --api-base "https://${TRAEFIK_API_HOST}/api/booking" \
  --event-create-mode if-empty \
  "${set_prices_args[@]}"
