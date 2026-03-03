from notification.domain.dto.create_notification_dto import CreateNotificationInput
from notification.domain.exceptions.notification_exception import EntityTypeEmpty


class NotificationValidator:
    @staticmethod
    def validate(input_dto: CreateNotificationInput) -> None:
        if not input_dto.entity_type.strip():
            raise EntityTypeEmpty()
