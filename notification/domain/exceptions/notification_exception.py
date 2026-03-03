from common.domain.exceptions.base_exception import DomainException


class EntityTypeEmpty(DomainException):
    def __init__(self) -> None:
        super().__init__('O tipo de entidade da notificacao nao pode ser vazio')


class NotificationSaveFailed(DomainException):
    def __init__(self, action: str, entity_type: str) -> None:
        self.action = action
        self.entity_type = entity_type
        super().__init__(
            f'Falha ao criar notificacao de "{action}" para "{entity_type}"'
        )
