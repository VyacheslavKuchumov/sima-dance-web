from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .realtime import seatmap_group_name


class SeatmapConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.group_name = seatmap_group_name(self.event_id)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send_json({
            'type': 'seatmap.ready',
            'event_id': self.event_id,
        })

    async def disconnect(self, close_code):
        if getattr(self, 'group_name', None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def seatmap_change(self, event):
        await self.send_json(event)
