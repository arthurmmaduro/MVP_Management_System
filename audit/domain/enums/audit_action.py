from enum import StrEnum


class AuditAction(StrEnum):
    CREATE = 'create'
    UPDATE = 'update'
    SOFT_DELETE = 'soft_delete'
    HARD_DELETE = 'hard_delete'
    VIEW = 'view'
