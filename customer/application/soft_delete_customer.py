import logging

from django.db import transaction

from audit.domain.exception.audit_exception import AuditSaveFailed
from customer.domain.dto.soft_delete_customer_dto import (
    SoftDeleteCustomerInput,
    SoftDeleteCustomerOutput,
)
from customer.domain.exceptions.customer_exceptions import (
    CustomerAuditOperationFailed,
    CustomerNotFound,
)
from customer.domain.repository.customer_audit_gateway import CustomerAuditGateway
from customer.domain.repository.customer_notification_gateway import (
    CustomerNotificationGateway,
)
from customer.domain.repository.customer_repository import CustomerRepository
from notification.domain.exceptions.notification_exception import NotificationSaveFailed

logger = logging.getLogger(__name__)


class SoftDeleteCustomerService:
    def __init__(
        self,
        repository: CustomerRepository,
        audit_gateway: CustomerAuditGateway,
        notification_gateway: CustomerNotificationGateway,
    ) -> None:
        self.repository = repository
        self.audit_gateway = audit_gateway
        self.notification_gateway = notification_gateway

    @transaction.atomic
    def execute(self, input_dto: SoftDeleteCustomerInput) -> SoftDeleteCustomerOutput:
        logger.info('Starting customer soft delete id=%s', input_dto.customer_id)
        customer = self.repository.get_by_id(input_dto.customer_id)
        if customer is None:
            logger.warning(
                'Customer not found for soft delete id=%s', input_dto.customer_id
            )
            raise CustomerNotFound(input_dto.customer_id)

        self.repository.soft_delete(
            customer_id=customer.id,
            updated_by=input_dto.updated_by,
        )
        try:
            self.audit_gateway.log_customer_deleted(
                customer_id=customer.id,
                deleted_by=input_dto.updated_by,
            )
        except AuditSaveFailed as exc:
            logger.exception(
                'Audit failure during customer soft delete customer_id=%s',
                customer.id,
            )
            raise CustomerAuditOperationFailed() from exc

        try:
            self.notification_gateway.notify_customer_deleted(
                customer_id=customer.id,
                triggered_by=input_dto.updated_by,
            )
        except NotificationSaveFailed:
            logger.exception(
                'Notification failure during customer soft delete customer_id=%s',
                customer.id,
            )

        logger.info('Customer soft deleted successfully id=%s', customer.id)
        return SoftDeleteCustomerOutput(customer_id=customer.id)
