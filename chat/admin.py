from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user', 'created_at', 'is_deleted', 'is_highlighted')
    list_filter = ('is_deleted', 'is_highlighted', 'created_at')
    search_fields = ('message', 'user__username')
    ordering = ('created_at',)
