from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from .models import Booking, Event, Seat
from .serializers import BookingSerializer


User = get_user_model()


class BookingFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.other_user = User.objects.create_user(username="bob", password="password123")
        self.staff_user = User.objects.create_user(username="admin", password="password123", is_staff=True)
        self.superuser = User.objects.create_superuser(username="root", password="password123", email="root@example.com")
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

    def assert_expires_in_about_30_minutes(self, expires_at):
        expected_expires_at = timezone.now() + timedelta(minutes=30)
        self.assertLessEqual(abs((expires_at - expected_expires_at).total_seconds()), 5)

    def test_user_can_release_held_booking(self):
        hold_response = self.hold_seat()
        self.assertEqual(hold_response.status_code, status.HTTP_201_CREATED)
        booking_id = hold_response.data["id"]

        booking = Booking.objects.get(pk=booking_id)
        self.assert_expires_in_about_30_minutes(booking.expires_at)

        release_response = self.client.post(reverse("release-booking", args=[booking_id]), format="json")

        self.assertEqual(release_response.status_code, status.HTTP_200_OK)
        self.assertEqual(release_response.data["id"], booking_id)
        self.assertFalse(Booking.objects.filter(pk=booking_id).exists())

    def test_booking_serializer_defaults_expires_at_to_thirty_minutes(self):
        factory = APIRequestFactory()
        request = factory.post("/", {}, format="json")
        request.user = self.user

        serializer = BookingSerializer(
            data={"seat_id": self.seat.id, "event_id": self.event.id},
            context={"request": request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        booking = serializer.save()

        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.status, Booking.STATUS_HELD)
        self.assert_expires_in_about_30_minutes(booking.expires_at)

    def test_confirm_allows_same_physical_seat_for_different_events(self):
        first_hold = self.hold_seat()
        first_booking_id = first_hold.data["id"]

        confirm_response = self.client.post(
            reverse("confirm-booking"),
            {"booking_ids": [first_booking_id]},
            format="json",
        )

        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        self.assertIsNone(Booking.objects.get(pk=first_booking_id).expires_at)

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

    def test_user_can_delete_booked_booking(self):
        hold_response = self.hold_seat()
        booking_id = hold_response.data["id"]

        confirm_response = self.client.post(
            reverse("confirm-booking"),
            {"booking_ids": [booking_id]},
            format="json",
        )
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)

        cancel_response = self.client.post(reverse("release-booking", args=[booking_id]), format="json")

        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel_response.data["id"], booking_id)
        self.assertFalse(Booking.objects.filter(pk=booking_id).exists())

        self.client.force_authenticate(self.other_user)
        next_hold_response = self.hold_seat()
        self.assertEqual(next_hold_response.status_code, status.HTTP_201_CREATED)

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

    def test_superuser_booking_list_defaults_to_current_user_only(self):
        Booking.create_hold(self.user, self.seat, self.event)
        other_seat = Seat.objects.create(section="Партер", row=1, number=2, price="1500.00")
        super_booking = Booking.create_hold(self.superuser, other_seat, self.event)

        self.client.force_authenticate(self.superuser)
        response = self.client.get(
            reverse("booking-list"),
            {"status": "held", "active_only": "true"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], super_booking.id)

    def test_superuser_can_request_all_users_bookings_explicitly(self):
        first_booking = Booking.create_hold(self.user, self.seat, self.event)
        other_seat = Seat.objects.create(section="Партер", row=1, number=2, price="1500.00")
        second_booking = Booking.create_hold(self.superuser, other_seat, self.event)

        self.client.force_authenticate(self.superuser)
        response = self.client.get(
            reverse("booking-list"),
            {"status": "held", "active_only": "true", "all_users": "true"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({item["id"] for item in response.data}, {first_booking.id, second_booking.id})

    def test_staff_cannot_request_all_users_bookings(self):
        Booking.create_hold(self.user, self.seat, self.event)

        self.client.force_authenticate(self.staff_user)
        response = self.client.get(
            reverse("booking-list"),
            {"status": "held", "active_only": "true", "all_users": "true"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_seatmap_includes_booking_status(self):
        self.hold_seat()

        self.client.force_authenticate(None)
        response = self.client.get(reverse("seat-map", args=[self.event.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["booking_status"], "held")
        self.assertIn("held_until", response.data[0])

    def test_events_endpoint_blocks_create_for_anonymous_user(self):
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

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_superuser_can_create_event(self):
        self.client.force_authenticate(self.superuser)
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

    def test_superuser_can_release_another_users_booking(self):
        hold_response = self.hold_seat()
        booking_id = hold_response.data["id"]

        self.client.force_authenticate(self.superuser)
        response = self.client.post(reverse("release-booking", args=[booking_id]), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Booking.objects.filter(pk=booking_id).exists())

    def test_superuser_can_assign_booking_through_admin_seat_endpoint(self):
        self.client.force_authenticate(self.superuser)
        response = self.client.post(
            reverse("admin-seat-booking", args=[self.event.id, self.seat.id]),
            {"user_id": self.other_user.id, "status": Booking.STATUS_BOOKED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user_id"], self.other_user.id)
        self.assertEqual(response.data["status"], Booking.STATUS_BOOKED)

    def test_superuser_cannot_assign_booking_when_seat_already_has_active_booking(self):
        Booking.create_hold(self.user, self.seat, self.event)

        self.client.force_authenticate(self.superuser)
        response = self.client.post(
            reverse("admin-seat-booking", args=[self.event.id, self.seat.id]),
            {"user_id": self.other_user.id, "status": Booking.STATUS_BOOKED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_admin_seat_endpoint_returns_current_booking(self):
        booking = Booking.create_hold(self.user, self.seat, self.event)

        self.client.force_authenticate(self.superuser)
        response = self.client.get(reverse("admin-seat-booking", args=[self.event.id, self.seat.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_booking"]["id"], booking.id)
        self.assertEqual(response.data["seat"]["id"], self.seat.id)
