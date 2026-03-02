from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from audit.domain.enums.audit_action import AuditAction
from audit.models.audit import Audit


class TestAuditModel(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create(
            username='audit-user',
            password='audit-password',
        )

    def test_create_audit_successfully(self):
        audit = Audit.objects.create(
            action=AuditAction.CREATE,
            entity_type='customer',
            entity_id=1,
            description='Cliente criado',
            metadata={'after': {'name': 'TestCustomer'}},
            created_by=self.user,
        )

        self.assertEqual(audit.action, AuditAction.CREATE.value)
        self.assertEqual(audit.entity_type, 'customer')
        self.assertEqual(audit.entity_id, 1)
        self.assertEqual(audit.description, 'Cliente criado')
        self.assertEqual(audit.metadata, {'after': {'name': 'TestCustomer'}})
        self.assertEqual(audit.created_by, self.user)
        self.assertIsNotNone(audit.created_at)

    def test_entity_id_can_be_null(self):
        audit = Audit.objects.create(
            action=AuditAction.CREATE,
            entity_type='product',
            entity_id=None,
            description='Produto criado',
            metadata={'after': {'name': 'TestProduct'}},
            created_by=self.user,
        )

        self.assertIsNone(audit.entity_id)

    def test_metadata_defaults_to_empty_dict(self):
        audit = Audit.objects.create(
            action=AuditAction.CREATE,
            entity_type='order',
            entity_id=1,
            description='Pedido criado',
            created_by=self.user,
        )

        self.assertEqual(audit.metadata, {})

    def test_created_by_is_required(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Audit.objects.create(
                    action=AuditAction.CREATE,
                    entity_type='order',
                    entity_id=1,
                    description='Pedido criado',
                )

    def test_string_representation(self):
        audit = Audit.objects.create(
            action=AuditAction.UPDATE,
            entity_type='order',
            entity_id=7,
            created_by=self.user,
        )

        self.assertEqual(str(audit), 'update order #7')
