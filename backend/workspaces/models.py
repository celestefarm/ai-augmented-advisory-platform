# workspaces/models.py

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Max, Q

User = get_user_model()


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class WorkspaceQuerySet(models.QuerySet):
    """Custom QuerySet for chainable methods"""
    
    def active(self):
        """Get active (non-archived) workspaces"""
        return self.filter(is_archived=False)
    
    def for_user(self, user):
        """Get workspaces for specific user"""
        return self.filter(user=user, is_archived=False)
    
    def with_counts(self):
        """Annotate with conversation and artifact counts"""
        return self.annotate(
            # Use different names to avoid conflicts
            total_conversations=Count(
                'conversations',
                filter=Q(conversations__is_archived=False)
            ),
            total_artifacts=Count(
                'artifacts',
                filter=Q(artifacts__is_archived=False)
            ),
            latest_activity=Max('conversations__last_message_at')
        )


class WorkspaceManager(models.Manager):
    """Custom manager using WorkspaceQuerySet"""
    
    def get_queryset(self):
        return WorkspaceQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)
    
    def with_counts(self):
        return self.get_queryset().with_counts()


class Workspace(BaseModel):
    """
    Workspace model for organizing conversations and artifacts
    Enterprise-ready with soft delete and ordering
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workspaces',
        db_index=True
    )
    name = models.CharField(
        max_length=255,
        help_text=_('Workspace name')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Optional workspace description')
    )
    icon = models.CharField(
        max_length=10,
        default='📁',
        help_text=_('Emoji icon for workspace')
    )
    color = models.CharField(
        max_length=7,
        default='#6366f1',
        help_text=_('Hex color code for workspace theme')
    )
    order = models.IntegerField(
        default=0,
        help_text=_('Display order (lower = first)')
    )
    is_archived = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_('Soft delete - archived workspaces')
    )
    is_pinned = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_('Pin workspace to top of list')
    )

    objects = WorkspaceManager()

    class Meta:
        db_table = 'workspaces'
        ordering = ['-is_pinned', 'order', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_archived']),
            models.Index(fields=['user', 'is_pinned']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(name__isnull=False) & ~models.Q(name=''),
                name='workspace_name_not_empty'
            )
        ]
        verbose_name = _('workspace')
        verbose_name_plural = _('workspaces')

    def __str__(self):
        return f"{self.icon} {self.name}"

    def clean(self):
        """Validate workspace limits"""
        if not self.pk:  # Only check on creation
            workspace_count = Workspace.objects.filter(
                user=self.user,
                is_archived=False
            ).count()
            
            if workspace_count >= self.user.workspace_limit:
                raise ValidationError(
                    _(f'You have reached your workspace limit of {self.user.workspace_limit}')
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)



class Artifact(BaseModel):
    """
    Artifact model for files/documents in workspace
    Supports various file types with metadata
    """
    FILE_TYPE_CHOICES = [
        ('document', _('Document')),
        ('spreadsheet', _('Spreadsheet')),
        ('presentation', _('Presentation')),
        ('image', _('Image')),
        ('pdf', _('PDF')),
        ('code', _('Code File')),
        ('other', _('Other')),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='artifacts',
        db_index=True
    )
    name = models.CharField(
        max_length=255,
        help_text=_('File name')
    )
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default='other'
    )
    file_url = models.URLField(
        help_text=_('URL to stored file (S3, etc.)')
    )
    file_size = models.BigIntegerField(
        default=0,
        help_text=_('File size in bytes')
    )
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('MIME type of file')
    )
    is_archived = models.BooleanField(
        default=False,
        help_text=_('Soft delete - archived artifacts')
    )

    class Meta:
        db_table = 'artifacts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'is_archived']),
        ]
        verbose_name = _('artifact')
        verbose_name_plural = _('artifacts')

    def __str__(self):
        return self.name