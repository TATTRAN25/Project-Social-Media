from django.urls import path
from .consumers import NotificationConsumer, LikeNotificationConsumer,PageLikeNotificationConsumer,ChatConsumer

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
    path('ws/likes/<int:post_id>/', LikeNotificationConsumer.as_asgi()),
    path('ws/likes/page/<int:page_id>/', PageLikeNotificationConsumer.as_asgi()),
    path('ws/chat/<int:receiver_id>/', ChatConsumer.as_asgi()),
]