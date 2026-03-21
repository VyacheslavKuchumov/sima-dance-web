from django.urls import path

from .consumers import SeatmapConsumer


websocket_urlpatterns = [
    path('ws/booking/events/<int:event_id>/seatmap/', SeatmapConsumer.as_asgi()),
]
