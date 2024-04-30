from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter

from django.core.asgi import get_asgi_application
from django.urls import path
from panel.consumers import WebSocket
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')




django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws', WebSocket.as_asgi())
        ])
    )
})