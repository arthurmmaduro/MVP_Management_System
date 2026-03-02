from collections.abc import Mapping

from audit.application.create_audit import CreateAuditService
from audit.domain.dto.create_audit_dto import CreateAuditInput
from audit.domain.enums.audit_action import AuditAction
from customer.domain.repository.customer_audit_gateway import CustomerAuditGateway


class CustomerAuditAdapter(CustomerAuditGateway):
    def __init__(self, create_audit_service: CreateAuditService) -> None:
        self._create_audit_service = create_audit_service

    def log_customer_created(self, *, customer_id: int, created_by: int) -> None:
        self._create_audit_service.execute(
            CreateAuditInput(
                action=AuditAction.CREATE,
                entity_type='customer',
                entity_id=customer_id,
                created_by=created_by,
                description='Cliente criado',
                metadata={},
            )
        )

    def log_customer_updated(
        self, *, customer_id: int, updated_by: int, metadata: Mapping[str, object]
    ) -> None:
        self._create_audit_service.execute(
            CreateAuditInput(
                action=AuditAction.UPDATE,
                entity_type='customer',
                entity_id=customer_id,
                created_by=updated_by,
                description='Cliente atualizado',
                metadata=metadata,
            )
        )

    def log_customer_deleted(self, *, customer_id: int, deleted_by: int) -> None:
        self._create_audit_service.execute(
            CreateAuditInput(
                action=AuditAction.SOFT_DELETE,
                entity_type='customer',
                entity_id=customer_id,
                created_by=deleted_by,
                description='Cliente excluído',
                metadata={},
            )
        )
