from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'creator',
        'category',
        'status',
        'scheduled_date',
        'is_featured',
        'created_at',
    )
    list_filter = (
        'category',
        'status',
        'is_featured',
        'created_at',
    )
    search_fields = (
        'title',
        'description',
        'tags',
        'creator__username',
    )
    date_hierarchy = 'scheduled_date'
    ordering = ('-created_at',)
