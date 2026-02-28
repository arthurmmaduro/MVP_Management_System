from customer.domain.exceptions.customer_exceptions import CustomerAlreadyExists
from customer.domain.value_objects.customer_name import CustomerName
from customer.models import Customer


def ensure_name_unique(name: CustomerName, customer_id: int | None = None) -> None:
    qs = Customer.objects.filter(name=name.name, is_active=True)

    if customer_id is not None:
        id: int = customer_id
        qs = qs.exclude(pk=id)

    if qs.exists():
        raise CustomerAlreadyExists(name.name)
