import logging

from customer.domain.dto.detail_customer_dto import (
    CustomerDetailInput,
    CustomerDetailOutput,
)
from customer.domain.exceptions.customer_exceptions import CustomerNotFound
from customer.domain.repository.customer_repository import CustomerRepository

logger = logging.getLogger(__name__)


class DetailCustomerService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def execute(self, input_dto: CustomerDetailInput) -> CustomerDetailOutput:
        logger.info('Starting customer detail id=%s', input_dto.customer_id)
        customer = self.repository.get_by_id(input_dto.customer_id)
        if customer is None:
            logger.warning('Customer not found for detail id=%s', input_dto.customer_id)
            raise CustomerNotFound(input_dto.customer_id)

        logger.info('Customer detail loaded successfully id=%s', customer.id)
        return CustomerDetailOutput(
            customer_id=customer.id,
            name=customer.name,
            created_by=customer.created_by_id,
            updated_by=customer.updated_by_id,
        )
