from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


SEATMAP_GROUP_PREFIX = 'seatmap.event'


def seatmap_group_name(event_id):
    return f'{SEATMAP_GROUP_PREFIX}.{event_id}'


def seatmap_change_payload(booking, action='upsert'):
    seat = booking.seat

    return {
        'type': 'seatmap.change',
        'action': action,
        'event_id': booking.event_id,
        'booking': {
            'id': booking.id,
            'seat_id': booking.seat_id,
            'event_id': booking.event_id,
            'user_id': booking.user_id,
            'status': booking.status,
            'created_at': booking.created_at.isoformat() if booking.created_at else None,
            'expires_at': booking.expires_at.isoformat() if booking.expires_at else None,
            'updated_at': booking.updated_at.isoformat() if booking.updated_at else None,
            'price_snapshot': str(booking.price_snapshot) if booking.price_snapshot is not None else None,
            'is_paid': booking.is_paid,
            'is_ticket_issued': booking.is_ticket_issued,
        },
        'seat': {
            'id': seat.id,
            'section': seat.section,
            'row': seat.row,
            'number': seat.number,
            'available': seat.available,
            'price': str(seat.price) if seat.price is not None else None,
        },
    }


def broadcast_seatmap_change(booking, action='upsert'):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return False

    async_to_sync(channel_layer.group_send)(
        seatmap_group_name(booking.event_id),
        seatmap_change_payload(booking, action=action),
    )
    return True
