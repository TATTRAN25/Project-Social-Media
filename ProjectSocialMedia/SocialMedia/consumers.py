import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "friendship_notifications",
            self.channel_name
        )
        await self.accept()
        print("Connected to WebSocket and added to group")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "friendship_notifications",
            self.channel_name
        )
        print("Disconnected from WebSocket and removed from group")

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "type": event["notification_type"],  # Sửa đổi từ "type" thành "notification_type"
            "request_id": event.get("request_id"),
            "from_user": event.get("from_user"),
        }))

    async def friend_request_sent(self, event):
        # Xử lý friend_request_sent, giống như send_notification
        await self.send_notification(event)

    async def connect(self):
        await self.channel_layer.group_add("friendship_notifications", self.channel_name)
        await self.accept()
        print(f"Connected: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("friendship_notifications", self.channel_name)
        print(f"Disconnected: {self.channel_name}")