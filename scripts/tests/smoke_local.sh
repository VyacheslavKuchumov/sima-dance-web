#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root_dir"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required to run smoke tests."
  exit 1
fi

wait_for_http() {
  local url="$1"
  local name="$2"

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

echo "Smoke tests passed."
