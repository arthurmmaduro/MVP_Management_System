from customer.domain.dto.create_customer_dto import CreateCustomerInput
from customer.domain.dto.update_customer_dto import UpdateCustomerInput
from customer.domain.rules.ensure_customer_name_is_unique import ensure_name_unique
from customer.domain.value_objects.customer_name import CustomerName


class CustomerNameValidator:
    @staticmethod
    def validate(
        input_dto: CreateCustomerInput | UpdateCustomerInput,
        *,
        customer_id: int | None = None,
    ) -> CustomerName:
        name = CustomerName.parse(input_dto.name)
        ensure_name_unique(name, customer_id=customer_id)
        return name
