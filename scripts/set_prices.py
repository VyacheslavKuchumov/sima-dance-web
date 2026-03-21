#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections.abc import Iterable
from datetime import date

import requests


DEFAULT_API_BASE = "http://127.0.0.1:8000/api/booking"


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


def build_rules() -> list[dict[str, object]]:
    rules: list[dict[str, object]] = []

    section = "Балкон"
    add_rule(rules, section, 7, 1, 26, 350, True)
    add_rule(rules, section, 6, 1, 24, 350, True)
    add_rule(rules, section, 5, 1, 24, 400, True)
    add_rule(rules, section, 4, 1, 24, 400, True)
    add_rule(rules, section, 3, 1, 24, 500, True)
    add_rule(rules, section, 2, 1, 28, 500, True)
    add_rule(rules, section, 1, 1, 28, 550, True)

    section = "Амфитеатр"
    add_rule(rules, section, 18, 1, 31, 350, True)
    add_rule(rules, section, 17, 1, 6, 350, True)
    add_rule(rules, section, 17, 7, 20, 400, True)
    add_rule(rules, section, 17, 21, 26, 350, True)
    add_rule(rules, section, 16, 1, 26, 400, True)
    add_rule(rules, section, 15, 1, 6, 400, True)
    add_rule(rules, section, 15, 7, 20, 500, True)
    add_rule(rules, section, 15, 21, 26, 400, True)
    add_rule(rules, section, 14, 1, 6, 400, True)
    add_rule(rules, section, 14, 7, 20, 500, True)
    add_rule(rules, section, 14, 21, 26, 400, True)
    add_rule(rules, section, 13, 2, 11, 550, True)
    add_rule(rules, section, 13, 16, 26, 550, True)

    section = "Партер"
    for row in range(6, 13):
        add_rule(rules, section, row, 1, 4, 400, True)
        add_rule(rules, section, row, 5, 8, 500, True)
        add_rule(rules, section, row, 9, 16, 550, True)
        add_rule(rules, section, row, 17, 20, 500, True)
        add_rule(rules, section, row, 21, 24, 400, True)

    add_rule(rules, section, 5, 1, 3, 400, True)
    add_rule(rules, section, 5, 4, 7, 500, True)
    add_rule(rules, section, 5, 8, 15, 550, True)
    add_rule(rules, section, 5, 16, 19, 500, True)
    add_rule(rules, section, 5, 20, 22, 400, True)
    add_rule(rules, section, 4, 1, 22, 550, True)
    add_rule(rules, section, 3, 1, 20, 550, True)
    add_rule(rules, section, 2, 1, 18, 550, True)
    add_rule(rules, section, 1, 1, 16, 550, True)

    add_rule(rules, "Балкон", 1, 13, 21, 550, False)
    add_rule(rules, "Балкон", 2, 15, 23, 500, False)
    add_rule(rules, "Балкон", 3, 13, 16, 500, False)
    add_rule(rules, "Партер", 5, 10, 11, 550, False)
    add_rule(rules, "Партер", 11, 13, 16, 550, False)
    add_rule(rules, "Партер", 1, 9, 9, 550, False)

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


def parse_args() -> argparse.Namespace:
    today = date.today().isoformat()
    parser = argparse.ArgumentParser(
        description="Create an event via REST API and configure global seat prices/availability.",
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
        help="Only update seat prices without creating a new event first.",
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

    if not args.skip_event_create:
        create_event(
            session=session,
            api_base=args.api_base.rstrip("/"),
            title=args.event_title,
            starts_at=args.event_date,
            img_url=args.event_image_url,
            archived=args.event_archived,
            timeout=args.timeout,
        )
        print("Note: seat prices are global in the current data model and apply to all events.")

    seats = get_seats(session, args.api_base.rstrip("/"), args.timeout)
    updated = 0
    skipped = 0

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
            api_base=args.api_base.rstrip("/"),
            seat=seat,
            price=target_price,
            available=target_available,
            timeout=args.timeout,
        )
        updated += 1
        print(
            f"Updated {seat['section']}: {seat['row']}-{seat['number']} "
            f"-> price={target_price}, available={target_available}"
        )

    print(f"Done. Updated {updated} seats, skipped {skipped}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
