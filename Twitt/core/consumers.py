import json
import time
from channels.generic.websocket import WebsocketConsumer
from .models import Like, Post


class Consumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        while int(1) in Post.objects.all().values_list("no_of_likes", flat=True):
            self.send(text_data=json.dumps({"value": Like.objects.count()}))
            time.sleep(2)
        self.close()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        self.send(text_data=text_data)
        self.close()


import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"user_{self.user.id}"

        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        notification = event["notification"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"notification": notification}))
