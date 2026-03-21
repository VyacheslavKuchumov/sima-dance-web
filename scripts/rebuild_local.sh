#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

if [ ! -f "$root_dir/.env" ]; then
  cp "$root_dir/.env.example" "$root_dir/.env"
  echo "Created .env from .env.example. Please update POSTGRES_PASSWORD and DJANGO_SECRET_KEY."
fi

compose_files=(-f "$root_dir/docker-compose.yml" -f "$root_dir/docker-compose.local.yml")
services=(postgres backend frontend)

docker compose "${compose_files[@]}" down
docker compose "${compose_files[@]}" up -d --build --force-recreate "${services[@]}"
