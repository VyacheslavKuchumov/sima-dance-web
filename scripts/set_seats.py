#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

import requests

import set_prices


DEFAULT_API_BASE = "http://127.0.0.1:8000/api/booking"


def add_seat(seats: list[dict[str, object]], section: str, row: int, number: int) -> None:
    seats.append(
        {
            "section": section,
            "row": row,
            "number": number,
        }
    )


def build_seat_specs() -> list[dict[str, object]]:
    seats: list[dict[str, object]] = []

    section = "Балкон"
    for row in range(1, 8):
        max_number = 28 if row in range(1, 3) else 24 if row in range(3, 7) else 26
        for seat_num in range(1, max_number + 1):
            add_seat(seats, section, row, seat_num)

    section = "Амфитеатр"
    for seat_num in range(2, 12):
        add_seat(seats, section, 13, seat_num)
    for seat_num in range(16, 27):
        add_seat(seats, section, 13, seat_num)
    for row in range(14, 18):
        for seat_num in range(1, 27):
            add_seat(seats, section, row, seat_num)
    for seat_num in range(1, 32):
        add_seat(seats, section, 18, seat_num)

    section = "Партер"
    row_to_max_number = {
        1: 16,
        2: 18,
        3: 20,
        4: 22,
        5: 22,
    }
    for row in range(1, 13):
        max_number = row_to_max_number.get(row, 24)
        for seat_num in range(1, max_number + 1):
            add_seat(seats, section, row, seat_num)

    return seats


SEAT_SPECS = build_seat_specs()


def get_seats(session: requests.Session, api_base: str, timeout: float) -> list[dict]:
    response = session.get(f"{api_base}/seats/", timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return payload["results"]
    raise ValueError("Unexpected seats payload format")


def create_seat(session: requests.Session, api_base: str, seat: dict[str, object], timeout: float) -> dict:
    response = session.post(f"{api_base}/seats/", json=seat, timeout=timeout)
    response.raise_for_status()
    created = response.json()
    print(f"Created seat {created['section']}: {created['row']}-{created['number']}")
    return created


def seat_key(seat: dict[str, object]) -> tuple[str, int, int]:
    return (
        str(seat["section"]),
        int(seat["row"]),
        int(seat["number"]),
    )


def install_missing_seats(
    session: requests.Session,
    api_base: str,
    timeout: float,
) -> tuple[int, int]:
    existing_seats = get_seats(session, api_base, timeout)
    existing_keys = {seat_key(seat) for seat in existing_seats}
    created = 0
    skipped = 0

    for seat in SEAT_SPECS:
        key = seat_key(seat)
        if key in existing_keys:
            skipped += 1
            continue

        create_seat(session, api_base, seat, timeout)
        existing_keys.add(key)
        created += 1

    return created, skipped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create missing seats via REST API without duplicating existing ones.",
    )
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="Base booking API URL.")
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
    set_prices.authenticate_session(
        session=session,
        api_base=args.api_base.rstrip("/"),
        timeout=args.timeout,
        username=args.username or None,
        password=args.password or None,
    )
    created, skipped = install_missing_seats(session, args.api_base.rstrip("/"), args.timeout)
    print(f"Done. Created {created} seats, skipped {skipped} existing seats.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
