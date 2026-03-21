#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_file="$root_dir/.env.production"

web_host="${TRAEFIK_WEB_HOST:-}"
api_host="${TRAEFIK_API_HOST:-}"
acme_email="${TRAEFIK_ACME_EMAIL:-}"
postgres_user="${POSTGRES_USER:-postgres}"
postgres_db="${POSTGRES_DB:-sima_dance}"
postgres_port="${POSTGRES_PORT:-5433}"
superuser_username="${DJANGO_SUPERUSER_USERNAME:-admin}"
superuser_email="${DJANGO_SUPERUSER_EMAIL:-}"
overwrite=false

usage() {
  cat <<'EOF'
Usage:
  ./scripts/generate_prod_env.sh --email admin@example.com --web-host sima.example.com --api-host api.sima.example.com [options]

Options:
  --email EMAIL                 Email for Let's Encrypt.
  --web-host HOST              Frontend domain.
  --api-host HOST              Backend API domain.
  --output PATH                Output file path. Default: .env.production
  --postgres-user USER         Default: postgres
  --postgres-db NAME           Default: sima_dance
  --postgres-port PORT         Default: 5433
  --superuser-username USER    Default: admin
  --superuser-email EMAIL      Default: same as --email
  --overwrite                  Overwrite existing output file.
  --help                       Show this help.
EOF
}

random_value() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    python -c 'import secrets; print(secrets.token_urlsafe(48))'
    return 0
  fi

  echo "openssl or python is required to generate secrets." >&2
  exit 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --email)
      acme_email="${2:-}"
      shift 2
      ;;
    --web-host)
      web_host="${2:-}"
      shift 2
      ;;
    --api-host)
      api_host="${2:-}"
      shift 2
      ;;
    --output)
      output_file="${2:-}"
      shift 2
      ;;
    --postgres-user)
      postgres_user="${2:-}"
      shift 2
      ;;
    --postgres-db)
      postgres_db="${2:-}"
      shift 2
      ;;
    --postgres-port)
      postgres_port="${2:-}"
      shift 2
      ;;
    --superuser-username)
      superuser_username="${2:-}"
      shift 2
      ;;
    --superuser-email)
      superuser_email="${2:-}"
      shift 2
      ;;
    --overwrite)
      overwrite=true
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

if [ -z "$web_host" ] || [ -z "$api_host" ] || [ -z "$acme_email" ]; then
  echo "Arguments --email, --web-host and --api-host are required." >&2
  usage >&2
  exit 1
fi

if [ -z "$superuser_email" ]; then
  superuser_email="$acme_email"
fi

if [ -e "$output_file" ] && [ "$overwrite" != true ]; then
  echo "File already exists: $output_file" >&2
  echo "Use --overwrite to replace it." >&2
  exit 1
fi

mkdir -p "$(dirname "$output_file")"

postgres_password="$(random_value)"
django_secret_key="$(random_value)"
superuser_password="$(random_value)"

allowed_hosts="backend,localhost,127.0.0.1,${web_host},${api_host}"
csrf_trusted_origins="https://${web_host},https://${api_host}"
cors_allowed_origins="https://${web_host}"

umask 077
cat >"$output_file" <<EOF
TRAEFIK_ACME_EMAIL=${acme_email}
TRAEFIK_WEB_HOST=${web_host}
TRAEFIK_API_HOST=${api_host}

POSTGRES_USER=${postgres_user}
POSTGRES_PASSWORD=${postgres_password}
POSTGRES_DB=${postgres_db}
POSTGRES_PORT=${postgres_port}

DJANGO_SECRET_KEY=${django_secret_key}
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=${allowed_hosts}
DJANGO_CSRF_TRUSTED_ORIGINS=${csrf_trusted_origins}
DJANGO_CORS_ALLOWED_ORIGINS=${cors_allowed_origins}

DJANGO_SUPERUSER_USERNAME=${superuser_username}
DJANGO_SUPERUSER_EMAIL=${superuser_email}
DJANGO_SUPERUSER_PASSWORD=${superuser_password}
EOF

chmod 600 "$output_file"

echo "Generated $output_file"
echo "TRAEFIK_WEB_HOST=$web_host"
echo "TRAEFIK_API_HOST=$api_host"
echo "DJANGO_SUPERUSER_USERNAME=$superuser_username"
echo "DJANGO_SUPERUSER_EMAIL=$superuser_email"
echo "The generated passwords are stored only in $output_file."
