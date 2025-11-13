from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'workspace', 'is_pinned', 'is_archived', 'last_message_at', 'created_at')
    list_filter = ('is_pinned', 'is_archived', 'workspace', 'created_at')
    search_fields = ('title', 'user__email', 'workspace__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_message_at')
    ordering = ('-created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'content_preview', 'tokens', 'created_at')
    list_filter = ('role', 'is_streaming', 'created_at')
    search_fields = ('content', 'conversation__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'