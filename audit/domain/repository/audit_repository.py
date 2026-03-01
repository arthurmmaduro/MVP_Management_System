from __future__ import annotations

from abc import ABC, abstractmethod

from audit.models import Audit


class AuditRepository(ABC):
    @abstractmethod
    def save(self, audit: Audit) -> None:
        raise NotImplementedError
