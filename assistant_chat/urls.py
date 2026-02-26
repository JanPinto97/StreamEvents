from django.urls import path
from .views import chat_page, chat_api

app_name = "assistant_chat"

urlpatterns = [
    path("assistant/", chat_page, name="page"),
    path("assistant/api/chat/", chat_api, name="api_chat"),
]