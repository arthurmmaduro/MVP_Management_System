from customer.domain.dto.list_customer_dto import CustomerListItem, CustomerListOutput
from customer.domain.repository.customer_repository import CustomerRepository


class ListCustomerService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def execute(self) -> CustomerListOutput:
        customers = [
            CustomerListItem(customer_id=customer.id, name=customer.name)
            for customer in self.repository.list_active()
        ]

        return CustomerListOutput(customers=customers)
