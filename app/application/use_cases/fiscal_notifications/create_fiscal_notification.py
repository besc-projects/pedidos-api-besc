from app.domain.entities.fiscal_notification import FiscalNotification
from app.domain.protocols.fiscal_notification_repository import (
    FiscalNotificationRepositoryProtocol,
)
from app.schemas.fiscal_notifications import FiscalNotificationCreate


class CreateFiscalNotificationUseCase:
    """Register that a product's missing-fiscal-registration warning was sent.

    Idempotent by design: this marks a "1x forever" event (see
    besc-commercial-pre-orders), so calling it twice for the same part_number
    just returns the existing record instead of erroring — the caller doesn't
    need to check-then-create defensively.
    """

    def __init__(self, repository: FiscalNotificationRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: FiscalNotificationCreate) -> FiscalNotification:
        existing = await self._repository.get_by_part_number(data.part_number)
        if existing is not None:
            return existing

        notification = FiscalNotification(part_number=data.part_number)
        return await self._repository.create(notification)
