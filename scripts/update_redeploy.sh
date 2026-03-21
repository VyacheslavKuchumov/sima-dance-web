#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

remote="origin"
branch="main"
env_file="$root_dir/.env.production"
no_build=false
skip_set_prices=false

usage() {
  cat <<'EOF'
Usage:
  ./scripts/update_redeploy.sh [options]

Options:
  --remote NAME         Git remote. Default: origin
  --branch NAME         Git branch. Default: main
  --env-file PATH       Env file for docker compose. Default: .env.production
  --no-build            Skip image rebuild before start.
  --skip-set-prices     Skip automatic seat price update after deploy.
  --help                Show this help.

The script aborts if the git worktree is dirty.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --remote)
      remote="${2:-}"
      shift 2
      ;;
    --branch)
      branch="${2:-}"
      shift 2
      ;;
    --env-file)
      env_file="${2:-}"
      shift 2
      ;;
    --no-build)
      no_build=true
      shift
      ;;
    --skip-set-prices)
      skip_set_prices=true
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

if ! command -v git >/dev/null 2>&1; then
  echo "git is required to update the repository." >&2
  exit 1
fi

if [ -n "$(git status --short)" ]; then
  echo "Git worktree is dirty. Commit or stash changes before running update_redeploy." >&2
  exit 1
fi

echo "Fetching ${remote}/${branch}..."
git fetch "$remote" "$branch"

if git show-ref --verify --quiet "refs/heads/${branch}"; then
  git checkout "$branch"
else
  git checkout -b "$branch" --track "${remote}/${branch}"
fi

echo "Pulling latest ${remote}/${branch}..."
git pull --ff-only "$remote" "$branch"

deploy_args=(--env-file "$env_file")
if [ "$no_build" = true ]; then
  deploy_args+=(--no-build)
fi
if [ "$skip_set_prices" = true ]; then
  deploy_args+=(--skip-set-prices)
fi

echo "Running redeploy..."
bash "$root_dir/scripts/deploy.sh" "${deploy_args[@]}"
