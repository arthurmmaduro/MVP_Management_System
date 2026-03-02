from audit.domain.dto.create_audit_dto import CreateAuditInput, CreateAuditOutput
from audit.domain.repository.audit_repository import AuditRepository
from audit.domain.validator.audit_validator import AuditValidator
from audit.models import Audit


class CreateAuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

    def execute(self, input_dto: CreateAuditInput) -> CreateAuditOutput:

        AuditValidator.validate(input_dto)

        audit = Audit(
            action=input_dto.action,
            entity_type=input_dto.entity_type,
            entity_id=input_dto.entity_id,
            description=input_dto.description,
            metadata=input_dto.metadata,
            created_by_id=input_dto.created_by,
        )
        self.repository.save(audit=audit)
        return CreateAuditOutput(audit_id=audit.id)
