from django.conf import settings
from django.db import models, transaction
from django.db.models import Q, UniqueConstraint
from django.utils import timezone
from decimal import Decimal

User = settings.AUTH_USER_MODEL
DEFAULT_HOLD_SECONDS = 30 * 60

class Event(models.Model):
    """An event (movie screening, flight, concert) that has seats (global seats used across events)."""
    title = models.CharField("Название", max_length=255)
    img_url = models.URLField("Ссылка на изображение", blank=True)
    archived = models.BooleanField("В архиве", default=False)
    starts_at = models.DateField("Дата начала")
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"

    def __str__(self):
        return f"{self.title} @ {self.starts_at}"

class Seat(models.Model):
    """A global seat (position/identity) reused across events."""
    section = models.CharField("Секция", max_length=32)
    row = models.PositiveIntegerField("Ряд")
    number = models.PositiveIntegerField("Место")
    available = models.BooleanField("Доступно", default=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        # seats are unique by section/row/number (global)
        unique_together = ('section', 'row', 'number')
        ordering = ['section', 'row', 'number']
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self):
        return f"{self.section}: {self.row}-{self.number}"

class Booking(models.Model):
    """Booking/Reservation record representing a user reserving one or more seats for an event."""
    STATUS_HELD = 'held'        # temporary hold awaiting payment / confirm
    STATUS_BOOKED = 'booked'    # confirmed (paid or finalized)
    STATUS_EXPIRED = 'expired'  # hold expired by background job

    STATUS_CHOICES = [
        (STATUS_HELD, 'Удержание'),
        (STATUS_BOOKED, 'Подтверждено'),
        (STATUS_EXPIRED, 'Истекло'),
    ]

    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE, verbose_name="Пользователь")
    seat = models.ForeignKey(Seat, related_name='bookings', on_delete=models.CASCADE, verbose_name="Место")
    event = models.ForeignKey(Event, related_name='bookings', on_delete=models.CASCADE, verbose_name="Событие")
    status = models.CharField("Статус", max_length=16, choices=STATUS_CHOICES, default=STATUS_HELD)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    # expires_at: when a hold becomes invalid; null allowed only if you intentionally want indefinite hold
    expires_at = models.DateTimeField("Действует до", null=True, blank=True)
    # snapshot of seat price at time of hold/booking
    price_snapshot = models.DecimalField("Цена на момент бронирования", max_digits=10, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField("Оплачено", default=False)
    is_ticket_issued = models.BooleanField("Билет выписан", default=False)

    class Meta:
        # Prevent two confirmed bookings for the same seat (PostgreSQL conditional unique index)
        constraints = [
            UniqueConstraint(
                fields=['event', 'seat'],
                condition=Q(status='booked'),
                name='unique_booked_event_seat'
            )
        ]
        indexes = [
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['event', 'seat']),
        ]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"{self.user} - {self.seat} ({self.status})"

    @classmethod
    def create_hold(cls, user, seat, event, hold_seconds=DEFAULT_HOLD_SECONDS):
        """
        Atomically create (or extend) a held booking for a single seat.

        Args:
            user: User instance placing the hold.
            seat: Seat instance to hold.
            event: Event instance for which the seat is being held.
            hold_seconds: int seconds until the hold expires (default 1800).

        Returns:
            Booking instance (created or extended).

        Raises:
            ValueError: if seat already BOOKED for this event or actively HELD by someone else.
            Seat.DoesNotExist: if seat.pk is invalid (propagated from .get()).
        """
        now = timezone.now()
        expires_at = now + timezone.timedelta(seconds=hold_seconds)

        # Use an atomic transaction and lock the seat row to avoid race conditions.
        with transaction.atomic():
            # Lock the seat row
            locked_seat = (
                type(seat).objects.select_for_update(nowait=False).get(pk=seat.pk)
            )

            # If already booked for this event -> cannot hold
            if cls.objects.filter(
                seat=locked_seat, event=event, status=cls.STATUS_BOOKED
            ).exists():
                raise ValueError(f"Seat already booked for this event: {locked_seat}")

            # If another user's active hold exists -> cannot hold
            active_other_hold = cls.objects.filter(
                seat=locked_seat,
                event=event,
                status=cls.STATUS_HELD,
            ).exclude(user=user).filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            )
            if active_other_hold.exists():
                raise ValueError(f"Seat currently held by someone else for this event: {locked_seat}")

            # If this user already has an active hold for this seat+event -> extend it
            existing_hold = cls.objects.filter(
                seat=locked_seat,
                event=event,
                status=cls.STATUS_HELD,
                user=user,
            ).filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            ).first()

            # Snapshot current seat price (safe fallback)
            price_snapshot = locked_seat.price if locked_seat.price is not None else Decimal("0.00")

            if existing_hold:
                # Extend/refresh the existing hold
                existing_hold.expires_at = expires_at
                existing_hold.price_snapshot = price_snapshot
                # Only update the changed fields
                existing_hold.save(update_fields=["expires_at", "price_snapshot"])
                return existing_hold

            # Otherwise create a new hold
            booking = cls.objects.create(
                user=user,
                seat=locked_seat,
                event=event,
                status=cls.STATUS_HELD,
                expires_at=expires_at,
                price_snapshot=price_snapshot,
            )

            return booking

    def confirm(self):
        """
        Confirm this booking (atomic). Sets status to BOOKED.
        Should be called inside a transaction around payment/validation to avoid races.
        Returns self after saving.
        Raises ValueError if seat already booked by someone else (double-check).
        """
        if self.status == self.STATUS_BOOKED:
            return self

        with transaction.atomic():
            # Re-check uniqueness at DB level: if another booked exists, error
            exists = Booking.objects.select_for_update().filter(
                seat=self.seat,
                event=self.event,
                status=self.STATUS_BOOKED
            ).exclude(pk=self.pk).exists()
            if exists:
                raise ValueError(f"Seat already booked for this event: {self.seat}")
            self.status = self.STATUS_BOOKED
            self.updated_at = timezone.now()
            self.save(update_fields=['status', 'updated_at'])
        return self
