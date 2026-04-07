from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Event, Seat, Booking, DEFAULT_HOLD_SECONDS
from accounts.serializers import UserSerializer

User = get_user_model()


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "img_url", "archived", "starts_at", "created_at"]


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'section', 'row', 'number', 'available', 'price']
        read_only_fields = ['id']

    def validate(self, attrs):
        # If updating, include instance values not provided in payload
        section = attrs.get('section', getattr(self.instance, 'section', None))
        row = attrs.get('row', getattr(self.instance, 'row', None))
        number = attrs.get('number', getattr(self.instance, 'number', None))

        if section is None or row is None or number is None:
            # Let model field validators handle missing fields (they normally aren't missing)
            return attrs

        # Check uniqueness manually to provide a nice error message
        qs = Seat.objects.filter(section=section, row=row, number=number)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({
                'non_field_errors': [f"Seat {section} {row}-{number} already exists."]
            })
        return attrs


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_details = UserSerializer(source="user", read_only=True)
    seat = SeatSerializer(read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)
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
            "user_id",
            "user_details",
            "seat",
            "seat_id",
            "event",
            "event_id",
            "event_title",
            "status",
            "created_at",
            "updated_at",
            "expires_at",
            "price_snapshot",
            "is_paid",
            "is_ticket_issued",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_id",
            "user_details",
            "seat",
            "event",
            "status",
            "created_at",
            "updated_at",
            "price_snapshot",
            "is_paid",
            "is_ticket_issued",
        ]

    def create(self, validated_data):
        # Attach current user
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user

        seat = validated_data["seat"]
        # snapshot the price at booking time
        validated_data["price_snapshot"] = seat.price

        # auto-expire after 30 minutes when the caller does not provide an explicit expiry
        validated_data.setdefault("expires_at", timezone.now() + timezone.timedelta(seconds=DEFAULT_HOLD_SECONDS))

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


class AdminSeatAssignmentSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
    )
    status = serializers.ChoiceField(
        choices=[Booking.STATUS_HELD, Booking.STATUS_BOOKED],
        default=Booking.STATUS_BOOKED,
    )
    hold_minutes = serializers.IntegerField(
        min_value=1,
        max_value=24 * 60,
        required=False,
        default=30,
    )
