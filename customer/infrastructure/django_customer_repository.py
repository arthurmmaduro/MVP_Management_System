from __future__ import annotations

import logging

from django.db import DatabaseError, IntegrityError

from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerDeleteFailed,
    CustomerSaveFailed,
)
from customer.domain.repository.customer_repository import CustomerRepository
from customer.models import Customer

logger = logging.getLogger(__name__)


class DjangoCustomerRepository(CustomerRepository):
    def save(self, customer: Customer, update_fields: list[str] | None = None) -> None:
        try:
            customer.save(update_fields=update_fields)
        except IntegrityError as exc:
            logger.exception(
                'Integrity error while saving customer name=%s', customer.name
            )
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
            logger.info('Customer not found in repository id=%s', customer_id)
            return None

    def soft_delete(self, customer_id: int) -> None:
        try:
            Customer.all_objects.filter(id=customer_id).update(is_active=False)
        except DatabaseError as exc:
            logger.exception(
                'Database error while soft deleting customer id=%s', customer_id
            )
            raise CustomerDeleteFailed(customer_id=customer_id) from exc

    def list_active(self) -> list[Customer]:
        return list(Customer.objects.order_by_name())
