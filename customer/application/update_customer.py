import logging

from django.db import transaction

from audit.domain.exception.audit_exception import AuditSaveFailed
from customer.domain.dto.update_customer_dto import (
    UpdateCustomerInput,
    UpdateCustomerOutput,
)
from customer.domain.exceptions.customer_exceptions import (
    CustomerAuditOperationFailed,
    CustomerNotFound,
)
from customer.domain.repository.customer_audit_gateway import CustomerAuditGateway
from customer.domain.repository.customer_repository import CustomerRepository
from customer.domain.validator.customer_name_validator import CustomerNameValidator

logger = logging.getLogger(__name__)


class UpdateCustomerService:
    def __init__(
        self, repository: CustomerRepository, audit_gateway: CustomerAuditGateway
    ) -> None:
        self.repository = repository
        self.audit_gateway = audit_gateway

    @transaction.atomic
    def execute(self, input_dto: UpdateCustomerInput) -> UpdateCustomerOutput:
        logger.info('Starting customer update id=%s', input_dto.customer_id)
        customer = self.repository.get_by_id(input_dto.customer_id)
        if customer is None:
            logger.warning('Customer not found for update id=%s', input_dto.customer_id)
            raise CustomerNotFound(input_dto.customer_id)

        before = {
            'name': customer.name,
        }

        customer_name = CustomerNameValidator.validate(
            input_dto, customer_id=input_dto.customer_id
        )

        customer.name = customer_name.name
        customer.updated_by_id = input_dto.updated_by
        self.repository.save(customer=customer, update_fields=['name', 'updated_by_id'])

        after = {
            'name': customer.name,
        }

        metadata = {
            'before': before,
            'after': after,
        }

        try:
            self.audit_gateway.log_customer_updated(
                customer_id=customer.id,
                updated_by=input_dto.updated_by,
                metadata=metadata,
            )
        except AuditSaveFailed as exc:
            logger.exception(
                'Audit failure during customer update customer_id=%s',
                customer.id,
            )
            raise CustomerAuditOperationFailed() from exc

        logger.info('Customer updated successfully id=%s', customer.id)
        return UpdateCustomerOutput(customer_id=customer.id)
