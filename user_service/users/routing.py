from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path("ws/chat/<int:pk>/<str:token>/", consumers.ChatConsumer.as_asgi()),
]
