from __future__ import annotations

from django.db import IntegrityError

from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerSaveFailed,
)
from customer.domain.repository.customer_repository import CustomerRepository
from customer.models import Customer


class DjangoCustomerRepository(CustomerRepository):
    def save(self, customer: Customer, update_fields: list[str] | None = None) -> None:
        try:
            customer.save(update_fields=update_fields)
        except IntegrityError as exc:
            if (
                Customer.objects.filter(name=customer.name, is_active=True)
                .exclude(pk=customer.pk)
                .exists()
            ):
                raise CustomerAlreadyExists(customer.name) from exc

            raise CustomerSaveFailed(customer.name) from exc

    def get_by_id(self, customer_id: int) -> Customer | None:
        try:
            return Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return None
