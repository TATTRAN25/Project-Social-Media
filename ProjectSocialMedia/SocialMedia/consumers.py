import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProjectSocialMedia.settings")
django.setup()

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
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
            "type": event["notification_type"],
            "request_id": event.get("request_id"),
            "from_user": event.get("from_user"),
        }))

    async def friend_request_sent(self, event):
        await self.send_notification(event)

class LikeNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.group_name = f"user_likes_{self.post_id}"

        # Tham gia vào nhóm
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Rời khỏi nhóm khi ngắt kết nối
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def like_post(self, event):
        await self.send(text_data=json.dumps({
            'post_id': event['post_id'],
            'is_liked': event['is_liked'],  
            'likes_count': event['likes_count'],  
        }))

class PageLikeNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.page_id = self.scope['url_route']['kwargs']['page_id']
        self.group_name = f"user_likes_page_{self.page_id}"

        # Tham gia vào nhóm
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Rời khỏi nhóm khi ngắt kết nối
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def like_page(self, event):
        await self.send(text_data=json.dumps({
            'page_id': event['page_id'],
            'is_liked': event['is_liked'],
            'likes_count': event['likes_count'],
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.room_group_name = f'chat_{self.receiver_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = self.scope["user"].id
        receiver_id = self.receiver_id

        # Save message to database
        msg = await Message.objects.create(sender_id=sender_id, receiver_id=receiver_id, content=message)

        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg.content,
                'sender': sender_id,
                'timestamp': str(msg.timestamp)
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp,
        }))