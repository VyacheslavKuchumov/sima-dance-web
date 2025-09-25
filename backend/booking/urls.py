from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventViewSet,
    SeatViewSet,
    SeatMapView,
    HoldSeatsView,
    ConfirmBookingView,
    BookingViewSet,
)

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"seats", SeatViewSet, basename="seat")
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("", include(router.urls)),
    # seat map for a single event
    path("events/<int:event_id>/seatmap/", SeatMapView.as_view(), name="seat-map"),
    # hold and confirm endpoints
    path("hold/", HoldSeatsView.as_view(), name="hold-seats"),
    path("confirm/", ConfirmBookingView.as_view(), name="confirm-booking"),
]
