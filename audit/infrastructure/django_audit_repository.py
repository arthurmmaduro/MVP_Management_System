from __future__ import annotations

from django.db import IntegrityError

from audit.domain.exception.audit_exception import AuditSaveFailed
from audit.domain.repository.audit_repository import AuditRepository
from audit.models import Audit


class DjangoAuditRepository(AuditRepository):
    def save(self, audit: Audit) -> None:
        try:
            audit.save()
        except IntegrityError as exc:
            raise AuditSaveFailed(audit.action, audit.entity_type) from exc
