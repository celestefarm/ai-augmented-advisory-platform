import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Abstract base model providing common fields for all models.
    Every model will inherit from this to maintain consistency.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_('Unique identifier')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text=_('Timestamp when record was created')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Timestamp when record was last updated')
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_('Soft delete flag')
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def delete(self, using=None, keep_parents=False):
        """Soft delete - mark as deleted instead of removing from DB"""
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

    def hard_delete(self):
        """Actually delete from database"""
        super().delete()


class BaseModelManager(models.Manager):
    """Custom manager that filters out soft-deleted records by default"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def with_deleted(self):
        """Include soft-deleted records"""
        return super().get_queryset()
    
    def deleted_only(self):
        """Only soft-deleted records"""
        return super().get_queryset().filter(is_deleted=True)