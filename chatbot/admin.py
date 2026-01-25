from django.contrib import admin
from .models import ChatbotConfig


@admin.register(ChatbotConfig)
class ChatbotConfigAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'api_url', 'is_active', 'timeout_seconds', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['model_name', 'api_url']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('API Settings', {
            'fields': ('api_url', 'model_name', 'timeout_seconds')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

