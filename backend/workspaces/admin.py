from django.contrib import admin
from .models import Workspace, Artifact


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'icon', 'is_pinned', 'is_archived', 'created_at')
    list_filter = ('is_pinned', 'is_archived', 'created_at')
    search_fields = ('name', 'description', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ('name', 'workspace', 'file_type', 'file_size', 'is_archived', 'created_at')
    list_filter = ('file_type', 'is_archived', 'created_at')
    search_fields = ('name', 'workspace__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)