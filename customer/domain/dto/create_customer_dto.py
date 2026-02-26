from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CustomerCreateInput:
    name: str
    created_by: int
    updated_by: int


@dataclass(frozen=True, slots=True)
class CreateCustomerOutput:
    customer_id: int
