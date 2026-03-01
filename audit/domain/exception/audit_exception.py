from common.domain.exceptions.base_exception import DomainException


class AuditSaveFailed(DomainException):
    def __init__(self, action: str, entity_type: str) -> None:
        self.action = action
        self.entity_type = entity_type
        super().__init__(
            f'Falha ao criar o audit log de "{action}" para "{entity_type}"'
        )
