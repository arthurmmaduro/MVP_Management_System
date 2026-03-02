from unittest.mock import Mock

from django.db import IntegrityError
from django.test import SimpleTestCase

from audit.domain.exception.audit_exception import AuditSaveFailed
from audit.infrastructure.django_audit_repository import DjangoAuditRepository


class TestDjangoAuditRepository(SimpleTestCase):
    def test_save_raises_audit_save_failed_when_model_save_raises_integrity_error(self):
        repository = DjangoAuditRepository()
        audit = Mock()
        audit.action = 'create'
        audit.entity_type = 'customer'
        audit.save.side_effect = IntegrityError()

        with self.assertRaises(AuditSaveFailed):
            repository.save(audit)
