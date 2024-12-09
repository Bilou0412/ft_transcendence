from django.urls import re_path
from .consumers import LobbyConsumer, ChatConsumer

websocket_urlpatterns = [
	re_path(r'ws/lobby/', LobbyConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<chat_type>\w+)/(?P<chat_id>\w+)/$', ChatConsumer.as_asgi()),
]