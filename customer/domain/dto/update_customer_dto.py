from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UpdateCustomerInput:
    customer_id: int
    name: str
    updated_by: int


@dataclass(frozen=True, slots=True)
class UpdateCustomerOutput:
    customer_id: int
