import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
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


class ConversationQuerySet(models.QuerySet):
    """Custom QuerySet for chainable methods"""
    
    def active(self):
        """Get active (non-archived) conversations"""
        return self.filter(is_archived=False)
    
    def for_user(self, user):
        """Get conversations for specific user"""
        return self.filter(user=user, is_archived=False)
    
    def quick_chats(self, user):
        """Get quick chats (conversations without workspace)"""
        return self.filter(user=user, workspace__isnull=True, is_archived=False)
    
    def in_workspace(self, workspace):
        """Get conversations in specific workspace"""
        return self.filter(workspace=workspace, is_archived=False)
    
    def with_counts(self):
        """Annotate with message counts"""
        return self.annotate(
            message_count=Count('messages'),
            last_message_time=Max('messages__created_at')
        )


class ConversationManager(models.Manager):
    """Custom manager using ConversationQuerySet"""
    
    def get_queryset(self):
        return ConversationQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)
    
    def quick_chats(self, user):
        return self.get_queryset().quick_chats(user)
    
    def in_workspace(self, workspace):
        return self.get_queryset().in_workspace(workspace)
    
    def with_counts(self):
        return self.get_queryset().with_counts()


class Conversation(BaseModel):
    """
    Conversation model for chat threads
    Can belong to workspace or be orphaned (quick chat)
    """
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='conversations',
        null=True,
        blank=True,
        help_text=_('Parent workspace (null for quick chats)')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations',
        db_index=True
    )
    title = models.CharField(
        max_length=255,
        default='New Conversation',
        help_text=_('Conversation title (auto-generated from first message)')
    )
    summary = models.TextField(
        blank=True,
        help_text=_('AI-generated conversation summary')
    )
    is_archived = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_('Soft delete - archived conversations')
    )
    is_pinned = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_('Pin conversation to top of list')
    )
    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_('Timestamp of last message for sorting')
    )

    objects = ConversationManager()

    class Meta:
        db_table = 'conversations'
        ordering = ['-is_pinned', '-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['user', 'workspace', 'is_archived']),
            models.Index(fields=['user', 'is_archived', 'last_message_at']),
            models.Index(fields=['workspace', 'is_archived']),
        ]
        verbose_name = _('conversation')
        verbose_name_plural = _('conversations')

    def __str__(self):
        return self.title

    @property
    def message_count(self):
        """Get message count"""
        return self.messages.count()

    @property
    def is_quick_chat(self):
        """Check if conversation is a quick chat (not in workspace)"""
        return self.workspace is None

    def update_last_message_timestamp(self):
        """Update last_message_at when new message is added"""
        self.last_message_at = timezone.now()
        self.save(update_fields=['last_message_at'])


class Message(BaseModel):
    """
    Message model for conversation messages
    Supports streaming and token tracking
    """
    ROLE_CHOICES = [
        ('user', _('User')),
        ('assistant', _('Assistant')),
        ('system', _('System')),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        db_index=True
    )

    agent_response = models.OneToOneField(
        'agents.AgentResponse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='message'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        db_index=True
    )
    content = models.TextField(
        help_text=_('Message content')
    )
    tokens = models.IntegerField(
        default=0,
        help_text=_('Token count for this message')
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('AI model used (for assistant messages)')
    )
    is_streaming = models.BooleanField(
        default=False,
        help_text=_('Message is currently streaming')
    )

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['conversation', 'role']),
        ]
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update conversation's last_message_at
        self.conversation.update_last_message_timestamp()