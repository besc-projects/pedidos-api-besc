from app.domain.entities.fiscal_notification import FiscalNotification
from app.domain.exceptions import NotFoundException
from app.domain.protocols.fiscal_notification_repository import (
    FiscalNotificationRepositoryProtocol,
)


class GetFiscalNotificationUseCase:
    """Check whether a product's missing-fiscal-registration warning was already sent."""

    def __init__(self, repository: FiscalNotificationRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, part_number: str) -> FiscalNotification:
        notification = await self._repository.get_by_part_number(part_number)
        if notification is None:
            raise NotFoundException("Fiscal notification not found.")
        return notification
