from dataclasses import dataclass

from common.normalize_spaces import normalize_spaces
from customer.domain.constants.constants import (
    CUSTOMER_NAME_MAX_LENGTH,
    CUSTOMER_NAME_MIN_LENGTH,
)
from customer.domain.exceptions.customer_exceptions import (
    CustomerNameIsEmpty,
    CustomerNameIsTooLong,
    CustomerNameIsTooShort,
)


@dataclass(frozen=True, slots=True)
class CustomerName:
    name: str

    def __post_init__(self) -> None:
        normalized_name = normalize_spaces(self.name)
        self._validate_normalized(normalized_name)
        object.__setattr__(self, 'name', normalized_name)

    @classmethod
    def parse(cls, name: str) -> 'CustomerName':
        normalized_name = normalize_spaces(name)
        cls._validate_normalized(normalized_name)
        return cls(name=normalized_name)

    @staticmethod
    def _validate_normalized(name: str) -> None:
        if name == '':
            raise CustomerNameIsEmpty()

        if len(name) > CUSTOMER_NAME_MAX_LENGTH:
            raise CustomerNameIsTooLong(CUSTOMER_NAME_MAX_LENGTH)

        if len(name) < CUSTOMER_NAME_MIN_LENGTH:
            raise CustomerNameIsTooShort(CUSTOMER_NAME_MIN_LENGTH)

    def __str__(self) -> str:
        return self.name
