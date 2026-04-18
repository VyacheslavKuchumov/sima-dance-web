#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

import requests

import set_prices
import set_seats


def parse_args() -> argparse.Namespace:
    today = set_prices.date.today().isoformat()
    parser = argparse.ArgumentParser(
        description="Install booking data: create missing seats, optionally create an event, and overwrite seat prices.",
    )
    parser.add_argument("--api-base", default=set_prices.DEFAULT_API_BASE, help="Base booking API URL.")
    parser.add_argument(
        "--username",
        default=os.environ.get("DJANGO_SUPERUSER_USERNAME", ""),
        help="Superuser username for authenticated API writes. Defaults to DJANGO_SUPERUSER_USERNAME.",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("DJANGO_SUPERUSER_PASSWORD", ""),
        help="Superuser password for authenticated API writes. Defaults to DJANGO_SUPERUSER_PASSWORD.",
    )
    parser.add_argument(
        "--skip-seats",
        action="store_true",
        help="Skip creating missing seats.",
    )
    parser.add_argument(
        "--skip-prices",
        action="store_true",
        help="Skip overwriting seat prices and availability.",
    )
    parser.add_argument(
        "--event-create-mode",
        choices=("always", "if-empty", "never"),
        default="if-empty",
        help="Event creation strategy. Default: if-empty.",
    )
    parser.add_argument(
        "--event-title",
        default=f"Тестовое событие {today}",
        help="Event title when creation is needed.",
    )
    parser.add_argument(
        "--event-date",
        default=today,
        help="Event date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--event-image-url",
        default="",
        help="Optional image URL for a created event.",
    )
    parser.add_argument(
        "--event-archived",
        action="store_true",
        help="Create the event in archived state.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification for HTTPS requests.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    session = requests.Session()
    set_prices.configure_session_tls(session, args.insecure)
    api_base = args.api_base.rstrip("/")
    set_prices.authenticate_session(
        session=session,
        api_base=api_base,
        timeout=args.timeout,
        username=args.username or None,
        password=args.password or None,
    )

    seats_created = 0
    seats_skipped = 0
    if args.skip_seats:
        print("Skipping seat installation.")
    else:
        seats_created, seats_skipped = set_seats.install_missing_seats(session, api_base, args.timeout)
        print(f"Seat installation done. Created {seats_created}, skipped {seats_skipped}.")

    created_event = set_prices.ensure_event(
        session=session,
        api_base=api_base,
        title=args.event_title,
        starts_at=args.event_date,
        img_url=args.event_image_url,
        archived=args.event_archived,
        timeout=args.timeout,
        create_mode=args.event_create_mode,
    )
    if created_event is not None:
        print("Note: seat prices are global in the current data model and apply to all events.")

    prices_updated = 0
    prices_skipped = 0
    if args.skip_prices:
        print("Skipping price installation.")
    else:
        prices_updated, prices_skipped = set_prices.apply_prices(session, api_base, args.timeout)
        print(f"Price installation done. Overwrote {prices_updated}, skipped {prices_skipped}.")

    print(
        "Install data finished. "
        f"Seats created: {seats_created}, seats skipped: {seats_skipped}, "
        f"event created: {'yes' if created_event is not None else 'no'}, "
        f"prices updated: {prices_updated}, prices skipped: {prices_skipped}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
