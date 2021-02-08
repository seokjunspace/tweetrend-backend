from django.urls import path
from . import consumers

websocket_urlpatterns = [
        path('ws/feed/<str:topic>/', consumers.FeedConsumer.as_asgi()),
]
