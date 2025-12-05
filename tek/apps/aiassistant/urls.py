from django.urls import path
from .views import ChatBotAPI

urlpatterns = [
    path("chat/", ChatBotAPI.as_view(), name="chat_api"),
]
