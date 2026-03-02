from common.domain.exceptions.base_exception import DomainException


class CustomerAlreadyExists(DomainException):
    def __init__(self, name: str) -> None:
        super().__init__(f'Já existe um cliente cadastrado com o nome {name}')


class CustomerNameIsEmpty(DomainException):
    def __init__(self) -> None:
        super().__init__('O nome do cliente não pode estar vazio')


class CustomerNameIsTooLong(DomainException):
    def __init__(self, max_length: int) -> None:
        super().__init__(
            f'O nome do cliente não pode ter mais de {max_length} caracteres'
        )


class CustomerNameIsTooShort(DomainException):
    def __init__(self, min_length: int) -> None:
        super().__init__(
            f'O nome do cliente não pode ter menos de {min_length} caracteres'
        )


class CustomerSaveFailed(DomainException):
    def __init__(self, name: str) -> None:
        super().__init__(f'Erro ao salvar o cliente: {name}')


class CustomerCreateFailed(DomainException):
    def __init__(self) -> None:
        super().__init__('Nao foi possível cadastrar o cliente')


class CustomerAuditOperationFailed(CustomerCreateFailed):
    def __init__(self) -> None:
        super().__init__()


class CustomerNotFound(DomainException):
    def __init__(self, customer_id: int) -> None:
        super().__init__(f'Cliente não encontrado: {customer_id}')


class CustomerDeleteFailed(DomainException):
    def __init__(self, customer_id: int) -> None:
        super().__init__(f'Erro ao deletar o cliente: {customer_id}')
