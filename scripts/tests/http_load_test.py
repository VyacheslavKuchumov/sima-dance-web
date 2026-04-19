#!/usr/bin/env python3
"""
Locust сценарий для Nuxt frontend:

1. Пользователь получает список групп регистрации.
2. Регистрируется через `/api/backend/accounts/signup/`.
3. Логинится через `/api/backend/accounts/token/`.
4. Находит событие по названию.
5. Загружает схему мест и выбирает 1..N свободных мест.
6. Открывает "Мои брони" через тот же API, что использует frontend.
7. Подтверждает удержанные места.

Запуск:
  pip install locust
  locust -f scripts/tests/http_load_test.py --host http://localhost:3000

Полезные переменные окружения:
  LOAD_TEST_EVENT_TITLE="Тестовое событие 2026-04-18"
  LOAD_TEST_MIN_SEATS=1
  LOAD_TEST_MAX_SEATS=2
  LOAD_TEST_MAX_HOLD_ATTEMPTS=8
  LOAD_TEST_PASSWORD="LoadTest123!"
"""

from __future__ import annotations

import json
import os
import random
import time
import uuid
from typing import Any

from locust import HttpUser, between, task


DEFAULT_EVENT_TITLE = "Тестовое событие 2026-04-18"
DEFAULT_PASSWORD = "LoadTest123!"
DEFAULT_PAYMENT_REFERENCE = "LOAD-TEST-QR"


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


EVENT_TITLE = os.getenv("LOAD_TEST_EVENT_TITLE", DEFAULT_EVENT_TITLE).strip() or DEFAULT_EVENT_TITLE
PASSWORD = os.getenv("LOAD_TEST_PASSWORD", DEFAULT_PASSWORD)
PAYMENT_REFERENCE = os.getenv("LOAD_TEST_PAYMENT_REFERENCE", DEFAULT_PAYMENT_REFERENCE)
MIN_SEATS = max(1, env_int("LOAD_TEST_MIN_SEATS", 1))
MAX_SEATS = max(MIN_SEATS, env_int("LOAD_TEST_MAX_SEATS", 2))
MAX_HOLD_ATTEMPTS = max(1, env_int("LOAD_TEST_MAX_HOLD_ATTEMPTS", 8))


class FrontendBookingUser(HttpUser):
    wait_time = between(1, 4)

    def on_start(self) -> None:
        self.auth_headers: dict[str, str] = {}

    @task
    def full_signup_hold_confirm_flow(self) -> None:
        self.auth_headers = {}
        signup_page_opened = self.open_signup_page()
        if not signup_page_opened:
            return

        group = self.fetch_signup_group()
        if not group:
            return

        username = self.build_username()
        password = PASSWORD

        registered = self.register_user(
            username=username,
            password=password,
            group_id=group["id"],
        )
        if not registered:
            return

        logged_in = self.login(username=username, password=password)
        if not logged_in:
            return

        user = self.fetch_current_user()
        if not user:
            return

        event = self.fetch_target_event()
        if not event:
            return

        event_id = event["id"]
        event_detail = self.fetch_event_detail(event_id)
        if not event_detail:
            return

        seats = self.fetch_seatmap(event_id)
        if not seats:
            return

        selected_booking_ids = self.hold_available_seats(event_id, seats)
        if not selected_booking_ids:
            return

        self.open_cart(event_id)
        self.confirm_bookings(event_id, selected_booking_ids)
        self.open_cart(event_id)

    def open_signup_page(self) -> bool:
        with self.client.get(
            "/signup",
            name="GET /signup",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"signup page failed: {response.status_code}")
                return False

            response.success()
            return True

    def build_username(self) -> str:
        suffix = uuid.uuid4().hex[:12]
        return f"load_{suffix}"

    def fetch_signup_group(self) -> dict[str, Any] | None:
        with self.client.get(
            "/api/backend/accounts/signup-groups/",
            name="GET /api/backend/accounts/signup-groups/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"signup-groups returned {response.status_code}")
                return None

            groups = self.parse_json(response)
            if not isinstance(groups, list) or not groups:
                response.failure("signup-groups returned empty payload")
                return None

            response.success()
            return random.choice(groups)

    def register_user(self, *, username: str, password: str, group_id: int) -> bool:
        payload = {
            "username": username,
            "password": password,
            "group": group_id,
            "full_name": f"Нагрузочный {username}",
            "child_full_name": f"Ребенок {username}",
        }

        with self.client.post(
            "/api/backend/accounts/signup/",
            json=payload,
            name="POST /api/backend/accounts/signup/",
            catch_response=True,
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(f"signup failed: {response.status_code} {response.text[:300]}")
                return False

            response.success()
            return True

    def login(self, *, username: str, password: str) -> bool:
        with self.client.post(
            "/api/backend/accounts/token/",
            json={"username": username, "password": password},
            name="POST /api/backend/accounts/token/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"token failed: {response.status_code} {response.text[:300]}")
                return False

            payload = self.parse_json(response)
            access = payload.get("access") if isinstance(payload, dict) else None
            if not access:
                response.failure("token response missing access token")
                return False

            self.auth_headers = {"Authorization": f"Bearer {access}"}
            response.success()
            return True

    def fetch_current_user(self) -> dict[str, Any] | None:
        with self.client.get(
            "/api/backend/accounts/me/",
            headers=self.auth_headers,
            name="GET /api/backend/accounts/me/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"me failed: {response.status_code}")
                return None

            payload = self.parse_json(response)
            if not isinstance(payload, dict) or not payload.get("id"):
                response.failure("me response missing user id")
                return None

            response.success()
            return payload

    def fetch_target_event(self) -> dict[str, Any] | None:
        with self.client.get(
            "/api/backend/booking/events/",
            name="GET /api/backend/booking/events/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"events failed: {response.status_code}")
                return None

            payload = self.parse_json(response)
            events = payload if isinstance(payload, list) else payload.get("results", []) if isinstance(payload, dict) else []
            if not events:
                response.failure("events list is empty")
                return None

            exact_match = next((event for event in events if event.get("title") == EVENT_TITLE), None)
            partial_match = next(
                (event for event in events if EVENT_TITLE.lower() in str(event.get("title", "")).lower()),
                None,
            )
            event = exact_match or partial_match

            if not event:
                available_titles = ", ".join(str(item.get("title")) for item in events[:10])
                response.failure(f"target event '{EVENT_TITLE}' not found. Available: {available_titles}")
                return None

            response.success()
            return event

    def fetch_event_detail(self, event_id: int) -> dict[str, Any] | None:
        with self.client.get(
            f"/api/backend/booking/events/{event_id}/",
            name="GET /api/backend/booking/events/:id/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"event detail failed: {response.status_code}")
                return None

            payload = self.parse_json(response)
            if not isinstance(payload, dict) or payload.get("id") != event_id:
                response.failure("event detail payload is invalid")
                return None

            response.success()
            return payload

    def fetch_seatmap(self, event_id: int) -> list[dict[str, Any]] | None:
        with self.client.get(
            f"/api/backend/booking/events/{event_id}/seatmap/",
            name="GET /api/backend/booking/events/:id/seatmap/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"seatmap failed: {response.status_code}")
                return None

            payload = self.parse_json(response)
            if not isinstance(payload, list):
                response.failure("seatmap payload is not a list")
                return None

            response.success()
            return payload

    def hold_available_seats(self, event_id: int, seats: list[dict[str, Any]]) -> list[int]:
        target_count = random.randint(MIN_SEATS, MAX_SEATS)
        available_seats = [
            seat for seat in seats
            if seat.get("booking_status") == "available" and seat.get("available") is True
        ]

        if not available_seats:
            self.environment.events.request.fire(
                request_type="FLOW",
                name="booking/no-available-seats",
                response_time=0,
                response_length=0,
                exception=RuntimeError("No available seats left for the target event."),
            )
            return []

        random.shuffle(available_seats)
        held_booking_ids: list[int] = []
        attempted_seat_ids: set[int] = set()
        hold_conflicts = 0

        while len(held_booking_ids) < target_count and len(attempted_seat_ids) < min(len(available_seats), MAX_HOLD_ATTEMPTS):
            seat = next((item for item in available_seats if item["id"] not in attempted_seat_ids), None)
            if seat is None:
                break

            attempted_seat_ids.add(seat["id"])
            booking = self.hold_seat(event_id=event_id, seat_id=seat["id"])
            if booking is None:
                hold_conflicts += 1
                continue

            booking_id = booking.get("id")
            if booking_id:
                held_booking_ids.append(int(booking_id))

        if not held_booking_ids:
            self.environment.events.request.fire(
                request_type="FLOW",
                name="booking/hold-flow-failed",
                response_time=0,
                response_length=0,
                exception=RuntimeError(f"Could not hold any seat. Conflicts={hold_conflicts}"),
            )

        return held_booking_ids

    def hold_seat(self, *, event_id: int, seat_id: int) -> dict[str, Any] | None:
        started_at = time.perf_counter()
        with self.client.post(
            "/api/backend/booking/hold/",
            headers=self.auth_headers,
            json={"event_id": event_id, "seat_id": seat_id},
            name="POST /api/backend/booking/hold/",
            catch_response=True,
        ) as response:
            if response.status_code == 409:
                response.success()
                self.environment.events.request.fire(
                    request_type="BUSINESS",
                    name="booking/hold-conflict",
                    response_time=(time.perf_counter() - started_at) * 1000,
                    response_length=len(response.content or b""),
                    exception=None,
                )
                return None

            if response.status_code not in (200, 201):
                response.failure(f"hold failed: {response.status_code} {response.text[:300]}")
                return None

            payload = self.parse_json(response)
            if not isinstance(payload, dict) or not payload.get("id"):
                response.failure("hold payload missing booking id")
                return None

            response.success()
            return payload

    def open_cart(self, event_id: int) -> list[dict[str, Any]] | None:
        with self.client.get(
            "/api/backend/booking/bookings/",
            headers=self.auth_headers,
            params={
                "event_id": str(event_id),
                "status": "held,booked",
                "active_only": "true",
            },
            name="GET /api/backend/booking/bookings/?event_id=:id",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"bookings failed: {response.status_code}")
                return None

            payload = self.parse_json(response)
            bookings = payload if isinstance(payload, list) else payload.get("results", []) if isinstance(payload, dict) else []
            if not isinstance(bookings, list):
                response.failure("bookings payload is invalid")
                return None

            response.success()
            return bookings

    def confirm_bookings(self, event_id: int, booking_ids: list[int]) -> list[dict[str, Any]] | None:
        current_bookings = self.open_cart(event_id)
        if current_bookings is None:
            return None

        held_booking_ids = [
            int(item["id"])
            for item in current_bookings
            if item.get("status") == "held" and item.get("id") in booking_ids
        ]

        if not held_booking_ids:
            self.environment.events.request.fire(
                request_type="FLOW",
                name="booking/no-held-bookings-before-confirm",
                response_time=0,
                response_length=0,
                exception=None,
            )
            return None

        with self.client.post(
            "/api/backend/booking/confirm/",
            headers=self.auth_headers,
            json={
                "booking_ids": held_booking_ids,
                "payment_reference": PAYMENT_REFERENCE,
            },
            name="POST /api/backend/booking/confirm/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"confirm failed: {response.status_code} {response.text[:300]}")
                return None

            payload = self.parse_json(response)
            if not isinstance(payload, list) or not payload:
                response.failure("confirm payload is invalid")
                return None

            booked_count = sum(1 for item in payload if item.get("status") == "booked")
            if booked_count != len(held_booking_ids):
                response.failure(
                    f"confirm returned {booked_count} booked records for {len(held_booking_ids)} requested"
                )
                return None

            response.success()
            return payload

    @staticmethod
    def parse_json(response: Any) -> Any:
        try:
            return response.json()
        except json.JSONDecodeError:
            return None
