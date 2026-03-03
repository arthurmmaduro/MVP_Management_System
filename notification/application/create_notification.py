from notification.domain.dto.create_notification_dto import (
    CreateNotificationInput,
    CreateNotificationOutput,
)
from notification.domain.repository.notification_repository import (
    NotificationRepository,
)
from notification.domain.validators.notification_validator import (
    NotificationValidator,
)
from notification.models import Notification


class CreateNotificationService:
    def __init__(self, notification_repository: NotificationRepository) -> None:
        self._notification_repository = notification_repository

    def execute(self, input_dto: CreateNotificationInput) -> CreateNotificationOutput:
        NotificationValidator.validate(input_dto)

        notification = Notification(
            action=input_dto.action.value,
            entity_type=input_dto.entity_type,
            entity_id=input_dto.entity_id,
            triggered_by_id=input_dto.triggered_by,
            audience=input_dto.audience.value,
        )
        self._notification_repository.save(notification=notification)
        return CreateNotificationOutput(notification_id=notification.id)
