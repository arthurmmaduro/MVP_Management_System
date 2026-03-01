from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CustomerDetailInput:
    customer_id: int


@dataclass(frozen=True, slots=True)
class CustomerDetailOutput:
    customer_id: int
    name: str
    created_by: int
    updated_by: int
