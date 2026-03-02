from audit.domain.dto.create_audit_dto import CreateAuditInput
from audit.domain.exception.audit_exception import EntityTypeEmpty


class AuditValidator:
    @staticmethod
    def validate(input_dto: CreateAuditInput) -> None:
        if not input_dto.entity_type.strip():
            raise EntityTypeEmpty()
