from django.db import transaction

from customer.domain.dto.create_customer_dto import (
    CreateCustomerOutput,
    CustomerCreateInput,
)
from customer.models import Customer


class CreateCustomerService:
    @transaction.atomic
    def execute(self, input_dto: CustomerCreateInput) -> CreateCustomerOutput:
        customer = Customer(
            name=input_dto.name,
            created_by_id=input_dto.created_by,
            updated_by_id=input_dto.created_by,
        )
        customer.save()
        return CreateCustomerOutput(customer_id=customer.id)
