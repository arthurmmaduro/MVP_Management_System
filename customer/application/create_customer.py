import logging

from django.db import transaction

from customer.domain.dto.create_customer_dto import (
    CreateCustomerInput,
    CreateCustomerOutput,
)
from customer.domain.repository.customer_repository import CustomerRepository
from customer.domain.validator.customer_name_validator import CustomerNameValidator
from customer.models import Customer

logger = logging.getLogger(__name__)


class CreateCustomerService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    @transaction.atomic
    def execute(self, input_dto: CreateCustomerInput) -> CreateCustomerOutput:
        logger.info('Starting customer creation')
        customer_name = CustomerNameValidator.validate(input_dto)

        customer = Customer(
            name=customer_name.name,
            created_by_id=input_dto.created_by,
            updated_by_id=input_dto.created_by,
        )
        self.repository.save(customer=customer)

        logger.info('Customer created successfully id=%s', customer.id)
        return CreateCustomerOutput(customer_id=customer.id)
