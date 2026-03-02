from dataclasses import dataclass

from audit.domain.enums.audit_action import AuditAction


@dataclass(frozen=True, slots=True)
class CreateAuditInput:
    action: AuditAction
    entity_type: str
    entity_id: int | None
    description: str
    metadata: dict[str, object]
    created_by: int


@dataclass(frozen=True, slots=True)
class CreateAuditOutput:
    audit_id: int
