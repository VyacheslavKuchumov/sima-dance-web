#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
locust_file="$root_dir/scripts/tests/http_load_test.py"
venv_dir="$root_dir/.venv-loadtest"

host="${LOAD_TEST_HOST:-https://booking.simadancing.ru}"
users="${LOAD_TEST_USERS:-50}"
spawn_rate="${LOAD_TEST_SPAWN_RATE:-5}"
run_time="${LOAD_TEST_RUN_TIME:-20m}"
event_title="${LOAD_TEST_EVENT_TITLE:-Тестовое событие 2026-04-18}"
min_seats="${LOAD_TEST_MIN_SEATS:-1}"
max_seats="${LOAD_TEST_MAX_SEATS:-2}"
max_hold_attempts="${LOAD_TEST_MAX_HOLD_ATTEMPTS:-8}"
password="${LOAD_TEST_PASSWORD:-LoadTest123!}"
payment_reference="${LOAD_TEST_PAYMENT_REFERENCE:-LOAD-TEST-QR}"
stop_timeout="${LOAD_TEST_STOP_TIMEOUT:-30}"
html_report=""
csv_prefix=""
loglevel="${LOAD_TEST_LOGLEVEL:-INFO}"
headless=1

usage() {
  cat <<EOF
Usage:
  scripts/tests/run_load_test.sh [options]

Options:
  --host URL              Nuxt frontend URL. Default: ${host}
  --users N              Concurrent users. Default: ${users}
  --spawn-rate N         Users started per second. Default: ${spawn_rate}
  --run-time TIME        Test duration, e.g. 10m, 30m, 1h. Default: ${run_time}
  --event-title TEXT     Target event title. Default: ${event_title}
  --min-seats N          Min seats per user flow. Default: ${min_seats}
  --max-seats N          Max seats per user flow. Default: ${max_seats}
  --max-hold-attempts N  Max seat hold attempts per user flow. Default: ${max_hold_attempts}
  --password TEXT        Password for generated users. Default: ${password}
  --payment-ref TEXT     Payment reference sent to confirm endpoint. Default: ${payment_reference}
  --stop-timeout SEC     Seconds to wait for users to stop. Default: ${stop_timeout}
  --html FILE            Save HTML report.
  --csv PREFIX           Save CSV stats with this prefix.
  --loglevel LEVEL       Locust log level. Default: ${loglevel}
  --web                  Start Locust web UI instead of headless mode.
  -h, --help             Show this help.

Examples:
  scripts/tests/run_load_test.sh --users 50 --spawn-rate 5 --run-time 20m
  scripts/tests/run_load_test.sh --users 75 --spawn-rate 10 --run-time 20m --max-seats 2
  scripts/tests/run_load_test.sh --users 100 --spawn-rate 20 --run-time 8m --html reports/load.html
  scripts/tests/run_load_test.sh --web
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --host)
      host="${2:?Missing value for --host}"
      shift 2
      ;;
    --users)
      users="${2:?Missing value for --users}"
      shift 2
      ;;
    --spawn-rate)
      spawn_rate="${2:?Missing value for --spawn-rate}"
      shift 2
      ;;
    --run-time)
      run_time="${2:?Missing value for --run-time}"
      shift 2
      ;;
    --event-title)
      event_title="${2:?Missing value for --event-title}"
      shift 2
      ;;
    --min-seats)
      min_seats="${2:?Missing value for --min-seats}"
      shift 2
      ;;
    --max-seats)
      max_seats="${2:?Missing value for --max-seats}"
      shift 2
      ;;
    --max-hold-attempts)
      max_hold_attempts="${2:?Missing value for --max-hold-attempts}"
      shift 2
      ;;
    --password)
      password="${2:?Missing value for --password}"
      shift 2
      ;;
    --payment-ref)
      payment_reference="${2:?Missing value for --payment-ref}"
      shift 2
      ;;
    --stop-timeout)
      stop_timeout="${2:?Missing value for --stop-timeout}"
      shift 2
      ;;
    --html)
      html_report="${2:?Missing value for --html}"
      shift 2
      ;;
    --csv)
      csv_prefix="${2:?Missing value for --csv}"
      shift 2
      ;;
    --loglevel)
      loglevel="${2:?Missing value for --loglevel}"
      shift 2
      ;;
    --web)
      headless=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

if [ ! -f "$locust_file" ]; then
  echo "Locust file not found: $locust_file"
  exit 1
fi

if command -v locust >/dev/null 2>&1; then
  locust_bin="$(command -v locust)"
else
  if [ ! -x "$venv_dir/bin/locust" ]; then
    echo "Locust is not installed. Creating local virtualenv: $venv_dir"
    python3 -m venv "$venv_dir"
    "$venv_dir/bin/python" -m pip install --upgrade pip
    "$venv_dir/bin/python" -m pip install locust
  fi

  locust_bin="$venv_dir/bin/locust"
fi

export LOAD_TEST_EVENT_TITLE="$event_title"
export LOAD_TEST_MIN_SEATS="$min_seats"
export LOAD_TEST_MAX_SEATS="$max_seats"
export LOAD_TEST_MAX_HOLD_ATTEMPTS="$max_hold_attempts"
export LOAD_TEST_PASSWORD="$password"
export LOAD_TEST_PAYMENT_REFERENCE="$payment_reference"

if [ -n "$html_report" ]; then
  mkdir -p "$(dirname "$html_report")"
fi

if [ -n "$csv_prefix" ]; then
  mkdir -p "$(dirname "$csv_prefix")"
fi

echo "Starting load test:"
echo "  host:        $host"
echo "  backend:     https://booking-server.simadancing.ru via Nuxt /api/backend proxy"
echo "  users:       $users"
echo "  spawn rate:  $spawn_rate users/sec"
echo "  run time:    $run_time"
echo "  stop timeout:$stop_timeout sec"
echo "  event title: $LOAD_TEST_EVENT_TITLE"
echo "  seats/user:  $LOAD_TEST_MIN_SEATS-$LOAD_TEST_MAX_SEATS"
echo "  hold tries:  $LOAD_TEST_MAX_HOLD_ATTEMPTS"
echo "  html report: ${html_report:-disabled}"
echo "  csv prefix:  ${csv_prefix:-disabled}"
echo

locust_args=(
  -f "$locust_file"
  --host "$host"
  --users "$users"
  --spawn-rate "$spawn_rate"
  --stop-timeout "$stop_timeout"
  --loglevel "$loglevel"
)

if [ -n "$html_report" ]; then
  locust_args+=(--html "$html_report")
fi

if [ -n "$csv_prefix" ]; then
  locust_args+=(--csv "$csv_prefix")
fi

if [ "$headless" -eq 1 ]; then
  exec "$locust_bin" "${locust_args[@]}" \
    --headless \
    --run-time "$run_time" \
    --print-stats \
    --only-summary
fi

exec "$locust_bin" "${locust_args[@]}"
