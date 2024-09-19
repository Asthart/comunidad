# routing.py

from django.urls import re_path
from django.urls import path
from . import views
from . import consumers

websocket_urlpatterns = [
  path('ws/chat/<str:receptor_id>/', views.ChatWS.as_asgi()),
]