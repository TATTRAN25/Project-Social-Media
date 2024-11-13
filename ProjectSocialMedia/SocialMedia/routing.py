from django.urls import path
from .consumers import NotificationConsumer, LikeNotificationConsumer

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
    path('ws/likes/<int:post_id>/', LikeNotificationConsumer.as_asgi()),
]