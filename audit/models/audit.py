from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    CREATE = 'create', 'Create'
    UPDATE = 'update', 'Update'
    SOFT_DELETE = 'soft_delete', 'Soft Delete'
    HARD_DELETE = 'hard_delete', 'Hard Delete'
    VIEW = 'view', 'View'


class Audit(models.Model):
    action = models.CharField(max_length=50, choices=AuditAction.choices)
    entity_type = models.CharField(max_length=100)
    entity_id = models.BigIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_created_by',
    )

    class Meta:
        db_table = 'audit'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id'], name='idx_audit_entity'),
            models.Index(
                fields=['action', 'created_at'], name='idx_audit_action_created'
            ),
            models.Index(fields=['created_by'], name='idx_audit_created_by'),
        ]

    def __str__(self) -> str:
        identifier = f' #{self.entity_id}' if self.entity_id is not None else ''
        return f'{self.action} {self.entity_type}{identifier}'
