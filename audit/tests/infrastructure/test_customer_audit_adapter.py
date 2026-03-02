from unittest.mock import Mock

from django.test import SimpleTestCase

from audit.domain.dto.create_audit_dto import CreateAuditInput
from audit.domain.enums.audit_action import AuditAction
from audit.infrastructure.customer_audit_adapter import CustomerAuditAdapter


class TestCustomerAuditAdapter(SimpleTestCase):
    def test_log_customer_created_translates_to_create_audit_input(self):
        create_audit_service = Mock()
        adapter = CustomerAuditAdapter(create_audit_service)

        adapter.log_customer_created(customer_id=7, created_by=11)

        create_audit_service.execute.assert_called_once_with(
            CreateAuditInput(
                action=AuditAction.CREATE,
                entity_type='customer',
                entity_id=7,
                created_by=11,
                description='Cliente criado',
                metadata={},
            )
        )

    def test_log_customer_updated_translates_to_create_audit_input(self):
        create_audit_service = Mock()
        adapter = CustomerAuditAdapter(create_audit_service)
        metadata = {
            'before': {'name': 'Old Customer'},
            'after': {'name': 'Updated Customer'},
        }

        adapter.log_customer_updated(customer_id=7, updated_by=11, metadata=metadata)

        create_audit_service.execute.assert_called_once_with(
            CreateAuditInput(
                action=AuditAction.UPDATE,
                entity_type='customer',
                entity_id=7,
                created_by=11,
                description='Cliente atualizado',
                metadata=metadata,
            )
        )

    def test_log_customer_deleted_translates_to_create_audit_input(self):
        create_audit_service = Mock()
        adapter = CustomerAuditAdapter(create_audit_service)

        adapter.log_customer_deleted(customer_id=7, deleted_by=11)

        create_audit_service.execute.assert_called_once_with(
            CreateAuditInput(
                action=AuditAction.SOFT_DELETE,
                entity_type='customer',
                entity_id=7,
                created_by=11,
                description='Cliente excluído',
                metadata={},
            )
        )
