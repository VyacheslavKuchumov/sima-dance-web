from rest_framework import serializers
from django.utils import timezone
from django.conf import settings
from .models import Event, Seat, Booking

User = settings.AUTH_USER_MODEL


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "img_url", "archived", "starts_at", "created_at"]


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["id", "section", "row", "number", "price"]


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    seat = SeatSerializer(read_only=True)
    seat_id = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all(),
        write_only=True,
        source="seat"
    )
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
        write_only=True,
        source="event"
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "seat",
            "seat_id",
            "event",
            "event_id",
            "status",
            "created_at",
            "updated_at",
            "expires_at",
            "price_snapshot",
        ]
        read_only_fields = [
            "id",
            "user",
            "seat",
            "event",
            "status",
            "created_at",
            "updated_at",
            "price_snapshot",
        ]

    def create(self, validated_data):
        # Attach current user
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user

        seat = validated_data["seat"]
        # snapshot the price at booking time
        validated_data["price_snapshot"] = seat.price

        # auto-expire after e.g. 15 minutes (optional)
        validated_data.setdefault("expires_at", timezone.now() + timezone.timedelta(minutes=15))

        return super().create(validated_data)

    def validate(self, attrs):
        """
        Optionally ensure that booking seat and event are logically consistent.
        For example: allow seat to be reused across events, but you could
        add constraints if needed.
        """
        seat = attrs.get("seat")
        event = attrs.get("event")

        if not seat:
            raise serializers.ValidationError("A seat must be provided.")
        if not event:
            raise serializers.ValidationError("An event must be provided.")

        return attrs
