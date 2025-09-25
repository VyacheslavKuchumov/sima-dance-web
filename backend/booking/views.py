from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from .models import Event, Seat, Booking
from .serializers import EventSerializer, SeatSerializer, BookingSerializer

# Read-only Event viewset
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all().order_by("-starts_at")
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

# Read-only Seat viewset (optionally nested under Event)
class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Seat.objects.select_related("event").all().order_by("row", "number")
    serializer_class = SeatSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

# Seat map: returns seats plus booking/hold info for an event
class SeatMapView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, event_id):
        """
        GET /api/events/{event_id}/seatmap/
        returns list of seats with booked / held info for this event
        """
        event = get_object_or_404(Event, pk=event_id)
        seats = Seat.objects.all().order_by("section", "row", "number")

        bookings = Booking.objects.filter(event=event).select_related('user', 'seat')

        data = []
        for s in seats:
            available = s.available and not bookings.filter(seat=s.id, status=Booking.STATUS_BOOKED).exists() and not bookings.filter(seat=s.id, status=Booking.STATUS_HELD, expires_at__gt=timezone.now()).exists()
            user_id = None if not bookings.filter(seat=s.id).exists() else bookings.filter(seat=s.id).first().user.id
            price_snapshot = s.price

            data.append({
                "id": s.id,
                "section": s.section,
                "row": s.row,
                "number": s.number,
                "user_id": user_id,
                "available": available,
                "price": str(price_snapshot) if price_snapshot is not None else None,
            })

        return Response(data)


# Create holds for a list of seat ids
class HoldSeatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        POST /api/hold/
        body: { "seat_ids": [1,2,3], "hold_seconds": 300 }

        Returns created Booking objects (status held).
        """
        seat_ids = request.data.get("seat_ids") or []
        hold_seconds = int(request.data.get("hold_seconds", 300))
        if not seat_ids:
            return Response({"detail": "seat_ids required"}, status=status.HTTP_400_BAD_REQUEST)

        seats = Seat.objects.filter(id__in=seat_ids).select_related("event")
        if seats.count() != len(seat_ids):
            return Response({"detail": "One or more seats not found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bookings = Booking.create_hold(request.user, seats, hold_seconds=hold_seconds)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Confirm held bookings (after payment)
class ConfirmBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        POST /api/confirm/
        body: { "booking_ids": [..], "payment_reference": "..." }
        """
        booking_ids = request.data.get("booking_ids") or []
        payment_ref = request.data.get("payment_reference", "")
        if not booking_ids:
            return Response({"detail": "booking_ids required"}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        bookings_qs = Booking.objects.filter(id__in=booking_ids, user=request.user).select_for_update()
        with transaction.atomic():
            bookings = list(bookings_qs.select_related("seat", "event"))
            # Validate all bookings
            for b in bookings:
                if b.status != Booking.STATUS_HELD:
                    return Response({"detail": f"Booking not in held state: {b.id}"}, status=status.HTTP_400_BAD_REQUEST)
                if b.expires_at and b.expires_at < now:
                    return Response({"detail": f"Hold expired for booking: {b.id}"}, status=status.HTTP_400_BAD_REQUEST)
                # Double-check no other booked exists for the same seat
                if Booking.objects.filter(seat=b.seat, status=Booking.STATUS_BOOKED).exclude(id=b.id).exists():
                    return Response({"detail": f"Seat already booked: {b.seat.id}"}, status=status.HTTP_409_CONFLICT)

            # Mark as booked
            for b in bookings:
                b.status = Booking.STATUS_BOOKED
                b.expires_at = None
                if payment_ref:
                    b.payment_reference = payment_ref if hasattr(b, "payment_reference") else ""
                b.save()

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Booking viewset: users can list their bookings; admins can view all
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related("seat", "event", "user").all().order_by("-created_at")
    serializer_class = BookingSerializer

    def get_permissions(self):
        # Admins can see all; regular users only their own bookings
        if self.request.method in ("GET", "HEAD", "OPTIONS") and self.request.user and self.request.user.is_staff:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return Booking.objects.filter(user=user).select_related("seat", "event").order_by("-created_at")
        return super().get_queryset()

    def perform_create(self, serializer):
        # Creation through API should be via HoldSeatsView — but support direct create if needed
        serializer.save(user=self.request.user)
