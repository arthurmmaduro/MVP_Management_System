from __future__ import annotations

from abc import ABC, abstractmethod

from customer.models import Customer


class CustomerRepository(ABC):
    @abstractmethod
    def save(self, customer: Customer, update_fields: list[str] | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, customer_id: int) -> Customer | None:
        raise NotImplementedError

    @abstractmethod
    def soft_delete(self, customer_id: int) -> None:
        raise NotImplementedError
