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
