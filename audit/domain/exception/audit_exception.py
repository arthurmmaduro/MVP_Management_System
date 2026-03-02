from common.domain.exceptions.base_exception import DomainException


class AuditSaveFailed(DomainException):
    def __init__(self, action: str, entity_type: str) -> None:
        self.action = action
        self.entity_type = entity_type
        super().__init__(
            f'Falha ao criar o audit log de "{action}" para "{entity_type}"'
        )


class EntityTypeEmpty(DomainException):
    def __init__(self) -> None:
        super().__init__('O tipo de entidade do log de auditoria nao pode ser vazio')
