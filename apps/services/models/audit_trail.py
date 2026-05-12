from django.db import models
from django.conf import settings


class AuditTrail(models.Model):
    """Abstract base model providing created_by, created_at, updated_at, and updated_by fields."""
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)s_created',
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)s_updated',
        null=True,
    )

    class Meta:
        abstract = True