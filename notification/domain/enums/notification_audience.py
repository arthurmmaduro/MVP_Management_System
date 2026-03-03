from enum import StrEnum


class NotificationAudience(StrEnum):
    ALL = 'all'
    MANAGER = 'manager'
    ANALYST = 'analyst'
    SUPPORT = 'support'
