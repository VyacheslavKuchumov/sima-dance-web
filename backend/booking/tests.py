from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Booking, Event, Seat


User = get_user_model()


class BookingFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.other_user = User.objects.create_user(username="bob", password="password123")
        self.event = Event.objects.create(title="Spring Gala", starts_at=date(2026, 4, 1))
        self.other_event = Event.objects.create(title="Summer Gala", starts_at=date(2026, 4, 2))
        self.seat = Seat.objects.create(section="Партер", row=1, number=1, price="1500.00")
        self.client.force_authenticate(self.user)

    def hold_seat(self, event_id=None, seat_id=None):
        return self.client.post(
            reverse("hold-seats"),
            {"event_id": event_id or self.event.id, "seat_id": seat_id or self.seat.id},
            format="json",
        )

    def test_user_can_release_held_booking(self):
        hold_response = self.hold_seat()
        self.assertEqual(hold_response.status_code, status.HTTP_201_CREATED)
        booking_id = hold_response.data["id"]

        release_response = self.client.post(reverse("release-booking", args=[booking_id]), format="json")

        self.assertEqual(release_response.status_code, status.HTTP_200_OK)
        self.assertEqual(release_response.data["status"], Booking.STATUS_CANCELLED)

    def test_confirm_allows_same_physical_seat_for_different_events(self):
        first_hold = self.hold_seat()
        first_booking_id = first_hold.data["id"]

        confirm_response = self.client.post(
            reverse("confirm-booking"),
            {"booking_ids": [first_booking_id]},
            format="json",
        )

        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)

        second_hold = self.hold_seat(event_id=self.other_event.id)
        self.assertEqual(second_hold.status_code, status.HTTP_201_CREATED)

        second_confirm = self.client.post(
            reverse("confirm-booking"),
            {"booking_ids": [second_hold.data["id"]]},
            format="json",
        )

        self.assertEqual(second_confirm.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Booking.objects.filter(seat=self.seat, status=Booking.STATUS_BOOKED).count(),
            2,
        )

    def test_active_hold_blocks_other_user_until_released(self):
        self.assertEqual(self.hold_seat().status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(self.other_user)
        conflict_response = self.hold_seat()

        self.assertEqual(conflict_response.status_code, status.HTTP_409_CONFLICT)

    def test_booking_list_filters_active_holds_for_event(self):
        active_hold = Booking.create_hold(self.user, self.seat, self.event)
        expired_hold = Booking.objects.create(
            user=self.user,
            seat=self.seat,
            event=self.other_event,
            status=Booking.STATUS_HELD,
            expires_at=timezone.now() - timedelta(minutes=5),
            price_snapshot="1500.00",
        )

        response = self.client.get(
            reverse("booking-list"),
            {"status": "held", "event_id": self.event.id, "active_only": "true"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["event"], self.event.id)

    def test_seatmap_includes_booking_status(self):
        self.hold_seat()

        self.client.force_authenticate(None)
        response = self.client.get(reverse("seat-map", args=[self.event.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["booking_status"], "held")
        self.assertIn("held_until", response.data[0])

    def test_events_endpoint_allows_create(self):
        self.client.force_authenticate(None)
        response = self.client.post(
            reverse("event-list"),
            {
                "title": "Autumn Gala",
                "starts_at": "2026-05-01",
                "img_url": "",
                "archived": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Autumn Gala")
