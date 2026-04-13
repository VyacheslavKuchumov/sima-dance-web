#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections.abc import Iterable
from datetime import date

import requests


DEFAULT_API_BASE = "http://127.0.0.1:8000/api/booking"
PRICE_INCREASE = 50
PARTER_FRONT_ROWS_PRICE = 700


def add_rule(
    rules: list[dict[str, object]],
    section: str,
    row: int,
    seat_start: int,
    seat_end: int,
    price: int,
    available: bool,
) -> None:
    rules.append(
        {
            "section": section,
            "row": row,
            "seat_start": seat_start,
            "seat_end": seat_end,
            "price": price,
            "available": available,
        }
    )


def bumped(price: int) -> int:
    return price + PRICE_INCREASE


def build_rules() -> list[dict[str, object]]:
    rules: list[dict[str, object]] = []

    section = "Балкон"
    add_rule(rules, section, 7, 1, 26, bumped(350), True)
    add_rule(rules, section, 6, 1, 24, bumped(350), True)
    add_rule(rules, section, 5, 1, 24, bumped(400), True)
    add_rule(rules, section, 4, 1, 24, bumped(400), True)
    add_rule(rules, section, 3, 1, 24, bumped(500), True)
    add_rule(rules, section, 2, 1, 28, bumped(500), True)
    add_rule(rules, section, 1, 1, 28, bumped(550), True)

    section = "Амфитеатр"
    add_rule(rules, section, 18, 1, 31, bumped(350), True)
    add_rule(rules, section, 17, 1, 6, bumped(350), True)
    add_rule(rules, section, 17, 7, 20, bumped(400), True)
    add_rule(rules, section, 17, 21, 26, bumped(350), True)
    add_rule(rules, section, 16, 1, 26, bumped(400), True)
    add_rule(rules, section, 15, 1, 6, bumped(400), True)
    add_rule(rules, section, 15, 7, 20, bumped(500), True)
    add_rule(rules, section, 15, 21, 26, bumped(400), True)
    add_rule(rules, section, 14, 1, 6, bumped(400), True)
    add_rule(rules, section, 14, 7, 20, bumped(500), True)
    add_rule(rules, section, 14, 21, 26, bumped(400), True)
    add_rule(rules, section, 13, 2, 11, bumped(550), True)
    add_rule(rules, section, 13, 16, 26, bumped(550), True)

    section = "Партер"
    for row in range(6, 13):
        add_rule(rules, section, row, 1, 4, bumped(400), True)
        add_rule(rules, section, row, 5, 8, bumped(500), True)
        add_rule(rules, section, row, 9, 16, bumped(550), True)
        add_rule(rules, section, row, 17, 20, bumped(500), True)
        add_rule(rules, section, row, 21, 24, bumped(400), True)

    add_rule(rules, section, 5, 1, 3, bumped(400), True)
    add_rule(rules, section, 5, 4, 7, bumped(500), True)
    add_rule(rules, section, 5, 8, 15, bumped(550), True)
    add_rule(rules, section, 5, 16, 19, bumped(500), True)
    add_rule(rules, section, 5, 20, 22, bumped(400), True)
    add_rule(rules, section, 4, 1, 22, bumped(550), True)
    add_rule(rules, section, 3, 1, 20, PARTER_FRONT_ROWS_PRICE, True)
    add_rule(rules, section, 2, 1, 18, PARTER_FRONT_ROWS_PRICE, True)
    add_rule(rules, section, 1, 1, 16, PARTER_FRONT_ROWS_PRICE, True)

    add_rule(rules, "Балкон", 1, 13, 21, bumped(550), False)
    add_rule(rules, "Балкон", 2, 15, 23, bumped(500), False)
    add_rule(rules, "Балкон", 3, 13, 16, bumped(500), False)
    add_rule(rules, "Партер", 5, 10, 11, bumped(550), False)
    add_rule(rules, "Партер", 11, 13, 16, bumped(550), False)
    add_rule(rules, "Партер", 1, 9, 9, PARTER_FRONT_ROWS_PRICE, False)

    return rules


RULES = build_rules()


def create_event(
    session: requests.Session,
    api_base: str,
    title: str,
    starts_at: str,
    img_url: str,
    archived: bool,
    timeout: float,
) -> dict:
    response = session.post(
        f"{api_base}/events/",
        json={
            "title": title,
            "starts_at": starts_at,
            "img_url": img_url,
            "archived": archived,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    event = response.json()
    print(f"Created event #{event['id']}: {event['title']} ({event['starts_at']})")
    return event


def get_events(session: requests.Session, api_base: str, timeout: float) -> list[dict]:
    response = session.get(f"{api_base}/events/", timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return payload["results"]
    raise ValueError("Unexpected events payload format")


def get_seats(session: requests.Session, api_base: str, timeout: float) -> list[dict]:
    response = session.get(f"{api_base}/seats/", timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return payload["results"]
    raise ValueError("Unexpected seats payload format")


def find_target(seat: dict, rules: Iterable[dict[str, object]]) -> dict[str, object] | None:
    target = None
    for rule in rules:
        if (
            seat.get("section") == rule["section"]
            and seat.get("row") == rule["row"]
            and rule["seat_start"] <= seat.get("number", 0) <= rule["seat_end"]
        ):
            target = rule
    return target


def patch_seat(
    session: requests.Session,
    api_base: str,
    seat: dict,
    price: int,
    available: bool,
    timeout: float,
) -> None:
    response = session.patch(
        f"{api_base}/seats/{seat['id']}/",
        json={"price": price, "available": available},
        timeout=timeout,
    )
    response.raise_for_status()


def ensure_event(
    session: requests.Session,
    api_base: str,
    title: str,
    starts_at: str,
    img_url: str,
    archived: bool,
    timeout: float,
    create_mode: str,
) -> dict | None:
    if create_mode == "never":
        print("Skipping event creation.")
        return None

    if create_mode == "if-empty":
        events = get_events(session, api_base, timeout)
        if events:
            print(f"Skipping event creation because {len(events)} event(s) already exist.")
            return None

    return create_event(
        session=session,
        api_base=api_base,
        title=title,
        starts_at=starts_at,
        img_url=img_url,
        archived=archived,
        timeout=timeout,
    )


def apply_prices(session: requests.Session, api_base: str, timeout: float) -> tuple[int, int]:
    seats = get_seats(session, api_base, timeout)
    updated = 0
    skipped = 0

    print("Overwriting configured seat prices and availability where they differ from the rules.")

    for seat in seats:
        target = find_target(seat, RULES)
        if target is None:
            skipped += 1
            continue

        current_price = int(float(seat.get("price") or 0))
        current_available = bool(seat.get("available"))
        target_price = int(target["price"])
        target_available = bool(target["available"])

        if current_price == target_price and current_available == target_available:
            skipped += 1
            continue

        patch_seat(
            session=session,
            api_base=api_base,
            seat=seat,
            price=target_price,
            available=target_available,
            timeout=timeout,
        )
        updated += 1
        print(
            f"Updated {seat['section']}: {seat['row']}-{seat['number']} "
            f"-> price={target_price}, available={target_available}"
        )

    return updated, skipped


def parse_args() -> argparse.Namespace:
    today = date.today().isoformat()
    parser = argparse.ArgumentParser(
        description="Create an event via REST API and overwrite seat prices/availability using the configured rules.",
    )
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="Base booking API URL.")
    parser.add_argument(
        "--event-title",
        default=f"Тестовое событие {today}",
        help="Event title to create before pricing seats.",
    )
    parser.add_argument(
        "--event-date",
        default=today,
        help="Event date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--event-image-url",
        default="",
        help="Optional image URL for the new event.",
    )
    parser.add_argument(
        "--event-archived",
        action="store_true",
        help="Create the event in archived state.",
    )
    parser.add_argument(
        "--skip-event-create",
        action="store_true",
        help="Only overwrite seat prices without creating a new event first.",
    )
    parser.add_argument(
        "--event-create-mode",
        choices=("always", "if-empty", "never"),
        default="always",
        help="Event creation strategy. Default: always.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    session = requests.Session()
    api_base = args.api_base.rstrip("/")
    event_create_mode = "never" if args.skip_event_create else args.event_create_mode

    created_event = ensure_event(
        session=session,
        api_base=api_base,
        title=args.event_title,
        starts_at=args.event_date,
        img_url=args.event_image_url,
        archived=args.event_archived,
        timeout=args.timeout,
        create_mode=event_create_mode,
    )
    if created_event is not None:
        print("Note: seat prices are global in the current data model and apply to all events.")

    updated, skipped = apply_prices(session, api_base, args.timeout)
    print(f"Done. Updated {updated} seats, skipped {skipped}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
