import logging

from customer.domain.dto.list_customer_dto import CustomerListItem, CustomerListOutput
from customer.domain.repository.customer_repository import CustomerRepository

logger = logging.getLogger(__name__)


class ListCustomerService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def execute(self) -> CustomerListOutput:
        logger.info('Starting customer list')
        customers = [
            CustomerListItem(customer_id=customer.id, name=customer.name)
            for customer in self.repository.list_active()
        ]

        logger.info('Customer list loaded successfully count=%s', len(customers))
        return CustomerListOutput(customers=customers)
