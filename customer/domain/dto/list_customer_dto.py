from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CustomerListItem:
    customer_id: int
    name: str


@dataclass(frozen=True, slots=True)
class CustomerListOutput:
    customers: list[CustomerListItem]
