from django.urls import path, re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from samples.consumers import WebConsumer
from logger.consumers import LoginSocket, SetupSocket
from dashboard.consumers import EventDistpatcher

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            re_path(r'ws/dashboard', EventDistpatcher),
            re_path(r'ws/samples/messages', WebConsumer),
            re_path(r'ws/logger/login', LoginSocket),
            re_path(r'ws/logger/setup', SetupSocket)
        ]),
    )
})