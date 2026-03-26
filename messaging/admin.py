from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'participant1', 'participant2', 'last_message_at', 'created_at']
    # Keep admin pages lightweight; also helps prevent worker OOM.
    list_per_page = 25
    list_filter = ['created_at', 'last_message_at']
    search_fields = ['participant1__username', 'participant2__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('participant1', 'participant2')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'is_read', 'created_at']
    # Avoid FK filter on `conversation` (can be expensive due to COUNTs).
    list_filter = ['read_at', 'created_at']
    list_per_page = 25
    search_fields = ['content', 'sender__username']
    readonly_fields = ['created_at', 'updated_at', 'read_at']

    # `content` is a TextField; don't pull it into changelist pages unless needed.
    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('sender', 'conversation')
            .defer('content')
        )
    
    def is_read(self, obj):
        return obj.read_at is not None
    is_read.boolean = True
    is_read.short_description = 'Read'

