from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SoftDeleteCustomerInput:
    customer_id: int
    updated_by: int


@dataclass(frozen=True, slots=True)
class SoftDeleteCustomerOutput:
    customer_id: int
