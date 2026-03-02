import logging

from django.db import transaction

from audit.domain.exception.audit_exception import AuditSaveFailed
from customer.domain.dto.create_customer_dto import (
    CreateCustomerInput,
    CreateCustomerOutput,
)
from customer.domain.exceptions.customer_exceptions import CustomerAuditFailed
from customer.domain.repository.customer_audit_gateway import CustomerAuditGateway
from customer.domain.repository.customer_repository import CustomerRepository
from customer.domain.validator.customer_name_validator import CustomerNameValidator
from customer.models import Customer

logger = logging.getLogger(__name__)


class CreateCustomerService:
    def __init__(
        self, repository: CustomerRepository, audit_gateway: CustomerAuditGateway
    ) -> None:
        self.repository = repository
        self.audit_gateway = audit_gateway

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
        try:
            self.audit_gateway.log_customer_created(
                customer_id=customer.id, created_by=input_dto.created_by
            )
        except AuditSaveFailed as exc:
            logger.exception(
                'Audit failure during customer creation customer_id=%s',
                customer.id,
            )
            raise CustomerAuditFailed() from exc

        logger.info('Customer created successfully id=%s', customer.id)
        return CreateCustomerOutput(customer_id=customer.id)
