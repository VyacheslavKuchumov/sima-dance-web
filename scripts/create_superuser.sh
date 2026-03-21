#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

if [ -f "$root_dir/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$root_dir/.env"
  set +a
fi

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-sima_dance}"
POSTGRES_PORT="${POSTGRES_PORT:-5433}"

export DATABASE_URL="${DATABASE_URL:-postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}}"
export SECRET_KEY="${DJANGO_SECRET_KEY:-change_me}"
export DEBUG="${DJANGO_DEBUG:-True}"

backend_python="$root_dir/backend/.venv/bin/python"
if [ ! -x "$backend_python" ]; then
  backend_python="python"
fi

username="${DJANGO_SUPERUSER_USERNAME:-}"
email="${DJANGO_SUPERUSER_EMAIL:-}"
password="${DJANGO_SUPERUSER_PASSWORD:-}"

if [ -z "$username" ]; then
  read -r -p "Superuser username: " username
fi

if [ -z "$email" ]; then
  read -r -p "Superuser email: " email
fi

if [ -z "$password" ]; then
  read -r -s -p "Superuser password: " password
  echo
fi

if [ -z "$username" ] || [ -z "$email" ] || [ -z "$password" ]; then
  echo "Username, email, and password are required."
  exit 1
fi

echo "Applying migrations before creating superuser..."
(
  cd "$root_dir/backend"
  "$backend_python" manage.py migrate
  DJANGO_SUPERUSER_USERNAME="$username" \
  DJANGO_SUPERUSER_EMAIL="$email" \
  DJANGO_SUPERUSER_PASSWORD="$password" \
  "$backend_python" manage.py shell -c "
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
)

echo "Superuser is ready: ${username}"
