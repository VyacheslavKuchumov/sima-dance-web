#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

python_bin="$root_dir/scripts/.venv/bin/python"
if [ ! -x "$python_bin" ]; then
  if command -v python3 >/dev/null 2>&1; then
    python_bin="python3"
  else
    python_bin="python"
  fi
fi

exec "$python_bin" "$root_dir/scripts/set_seats.py" "$@"
