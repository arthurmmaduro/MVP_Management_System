from __future__ import annotations

from abc import ABC, abstractmethod


class CustomerAuditGateway(ABC):
    @abstractmethod
    def log_customer_created(self, *, customer_id: int, created_by: int) -> None:
        raise NotImplementedError

    def log_customer_updated(
        self, *, customer_id: int, updated_by: int, metadata: dict
    ) -> None:
        raise NotImplementedError

    def log_customer_deleted(self, *, customer_id: int, deleted_by: int) -> None:
        raise NotImplementedError
