from django.test import SimpleTestCase

from audit.domain.dto.create_audit_dto import CreateAuditInput
from audit.domain.enums.audit_action import AuditAction
from audit.domain.exception.audit_exception import EntityTypeEmpty
from audit.domain.validator.audit_validator import AuditValidator


class TestAuditValidator(SimpleTestCase):
    def test_validate_raises_when_entity_type_is_empty(self):
        input_dto = CreateAuditInput(
            action=AuditAction.CREATE,
            entity_type='   ',
            entity_id=1,
            description='Cliente criado',
            metadata={},
            created_by=1,
        )

        with self.assertRaises(EntityTypeEmpty):
            AuditValidator.validate(input_dto)
