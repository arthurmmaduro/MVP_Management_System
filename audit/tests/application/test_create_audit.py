from django.contrib.auth import get_user_model
from django.test import TestCase

from audit.application.create_audit import CreateAuditService
from audit.domain.dto.create_audit_dto import CreateAuditInput
from audit.domain.enums.audit_action import AuditAction
from audit.domain.exception.audit_exception import AuditSaveFailed
from audit.domain.repository.audit_repository import AuditRepository
from audit.infrastructure.django_audit_repository import DjangoAuditRepository
from audit.models import Audit


class TestCreateAuditService(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser_audit',
            password='testpassword',
        )
        self.repository = DjangoAuditRepository()

    def test_execute_creates_audit_and_returns_id(self):
        service = CreateAuditService(self.repository)
        input_dto = CreateAuditInput(
            action=AuditAction.CREATE,
            entity_type='customer',
            entity_id=1,
            description='Cliente criado',
            metadata={'after': {'name': 'Test Customer'}},
            created_by=self.user.id,
        )

        output = service.execute(input_dto)
        audit = Audit.objects.get(pk=output.audit_id)

        self.assertIsNotNone(output.audit_id)
        self.assertEqual(audit.action, AuditAction.CREATE.value)
        self.assertEqual(audit.entity_type, 'customer')
        self.assertEqual(audit.entity_id, 1)
        self.assertEqual(audit.description, 'Cliente criado')
        self.assertEqual(audit.metadata, {'after': {'name': 'Test Customer'}})
        self.assertEqual(audit.created_by_id, self.user.id)
        self.assertIsNotNone(audit.created_at)

    def test_execute_allows_entity_id_to_be_null(self):
        service = CreateAuditService(self.repository)

        output = service.execute(
            CreateAuditInput(
                action=AuditAction.VIEW,
                entity_type='dashboard',
                entity_id=None,
                description='Dashboard visualizado',
                metadata={},
                created_by=self.user.id,
            )
        )
        audit = Audit.objects.get(pk=output.audit_id)

        self.assertIsNone(audit.entity_id)

    def test_execute_raises_when_repository_save_fails(self):
        class FailingAuditRepository(AuditRepository):
            def save(self, audit: Audit) -> None:
                raise AuditSaveFailed(audit.action, audit.entity_type)

        service = CreateAuditService(FailingAuditRepository())

        with self.assertRaises(AuditSaveFailed):
            service.execute(
                CreateAuditInput(
                    action=AuditAction.UPDATE,
                    entity_type='customer',
                    entity_id=1,
                    description='Cliente atualizado',
                    metadata={'before': {'name': 'Old'}, 'after': {'name': 'New'}},
                    created_by=self.user.id,
                )
            )
