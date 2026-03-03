from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping


class CustomerNotificationGateway(ABC):
    @abstractmethod
    def notify_customer_created(self, *, customer_id: int, triggered_by: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def notify_customer_updated(
        self, *, customer_id: int, triggered_by: int, metadata: Mapping[str, object]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def notify_customer_deleted(self, *, customer_id: int, triggered_by: int) -> None:
        raise NotImplementedError
