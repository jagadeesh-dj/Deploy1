from django.urls import re_path
from chatapp import consumer

websocket_urlpatterns=[
    re_path(r'ws/chatroom/(?P<receiver>\w+)/$',consumer.chatconsumer.as_asgi()),
    re_path(R'ws/mainsocket/',consumer.Mainsocket.as_asgi())
]