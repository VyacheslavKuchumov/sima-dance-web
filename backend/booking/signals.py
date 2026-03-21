from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Booking
from .realtime import broadcast_seatmap_change


def _queue_seatmap_broadcast(booking, action='upsert'):
    transaction.on_commit(lambda: broadcast_seatmap_change(booking, action=action))


@receiver(post_save, sender=Booking, dispatch_uid='booking-seatmap-post-save')
def booking_post_save(sender, instance, created, **kwargs):
    _queue_seatmap_broadcast(instance, action='created' if created else 'updated')


@receiver(post_delete, sender=Booking, dispatch_uid='booking-seatmap-post-delete')
def booking_post_delete(sender, instance, **kwargs):
    _queue_seatmap_broadcast(instance, action='deleted')
