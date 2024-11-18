import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProjectSocialMedia.settings")
django.setup()

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from .models import Message
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
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

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.room_name = f"chat_{min(self.scope['user'].id, self.receiver_id)}_{max(self.scope['user'].id, self.receiver_id)}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('content')

        if message_content:
            sender = self.scope['user']
            receiver = User.objects.get(id=self.receiver_id)

            # Lưu tin nhắn vào cơ sở dữ liệu
            message = Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=message_content
            )

            # Gửi tin nhắn tới group
            async_to_sync(self.channel_layer.group_send)(
                self.room_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'sender': sender.username,
                    'content': message_content,
                    'timestamp': message.timestamp.strftime('%H:%M'),
                }
            )
        
        elif data.get('type') == 'delete_message':
            message_id = data['message_id']
            self.delete_message(message_id)

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'sender': event['sender'],
            'content': event['content'],
            'timestamp': event['timestamp'],
        }))
    
    def delete_message(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            # Kiểm tra quyền truy cập
            if message.sender == self.scope['user']:
                message.is_deleted = True
                message.save()

                # Gửi thông báo xóa tới group
                async_to_sync(self.channel_layer.group_send)(
                    self.room_name,
                    {
                        'type': 'delete_message_event',
                        'message_id': message.id,
                    }
                )
        except Message.DoesNotExist:
            print(f"Message with id {message_id} does not exist.")

    def delete_message_event(self, event):
        self.send(text_data=json.dumps({
            'type': 'delete_message',
            'message_id': event['message_id'],
        }))
