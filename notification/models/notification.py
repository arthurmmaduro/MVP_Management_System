from django.conf import settings
from django.db import models

from notification.domain.enums.notification_action import NotificationAction
from notification.domain.enums.notification_audience import NotificationAudience

NOTIFICATION_ACTION_CHOICES = [
    (action.value, action.name.replace('_', ' ').title())
    for action in NotificationAction
]

NOTIFICATION_AUDIENCE_CHOICES = [
    (audience.value, audience.name.replace('_', ' ').title())
    for audience in NotificationAudience
]


class Notification(models.Model):
    action = models.CharField(max_length=50, choices=NOTIFICATION_ACTION_CHOICES)
    entity_type = models.CharField(max_length=100)
    entity_id = models.BigIntegerField(null=True, blank=True)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_triggered_by',
    )
    audience = models.CharField(max_length=50, choices=NOTIFICATION_AUDIENCE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'
        indexes = [
            models.Index(fields=['action'], name='idx_notification_action'),
            models.Index(fields=['triggered_by'], name='idx_notification_triggered_by'),
        ]

    def __str__(self) -> str:
        identifier = f' #{self.entity_id}' if self.entity_id is not None else ''
        return f'{self.action} {self.entity_type}{identifier}'
