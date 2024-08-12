import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

django_asgi_app = get_asgi_application()

from users.routing import websocket_urlpatterns
from users.middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': TokenAuthMiddleware(URLRouter(websocket_urlpatterns))
})
