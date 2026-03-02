from enum import StrEnum


class NotificationAction(StrEnum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
