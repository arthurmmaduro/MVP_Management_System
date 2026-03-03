from django.test import SimpleTestCase

from notification.domain.dto.create_notification_dto import CreateNotificationInput
from notification.domain.enums.notification_action import NotificationAction
from notification.domain.enums.notification_audience import NotificationAudience
from notification.domain.exceptions.notification_exception import EntityTypeEmpty
from notification.domain.validators.notification_validator import (
    NotificationValidator,
)


class TestNotificationValidator(SimpleTestCase):
    def test_validate_does_not_raise_when_entity_type_is_valid(self):
        input_dto = CreateNotificationInput(
            action=NotificationAction.CREATE,
            entity_type='customer',
            entity_id=1,
            triggered_by=1,
            audience=NotificationAudience.MANAGER,
            description='Cliente criado',
            metadata={},
        )

        NotificationValidator.validate(input_dto)

    def test_validate_raises_when_entity_type_is_empty(self):
        input_dto = CreateNotificationInput(
            action=NotificationAction.CREATE,
            entity_type='   ',
            entity_id=1,
            triggered_by=1,
            audience=NotificationAudience.MANAGER,
            description='Descricao irrelevante',
            metadata={},
        )

        with self.assertRaises(EntityTypeEmpty):
            NotificationValidator.validate(input_dto)
