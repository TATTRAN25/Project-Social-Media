import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
import SocialMedia.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProjectSocialMedia.settings")
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            SocialMedia.routing.websocket_urlpatterns
        )
    ),
})