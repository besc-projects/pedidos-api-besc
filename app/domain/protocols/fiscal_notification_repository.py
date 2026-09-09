from typing import Optional, Protocol

from app.domain.entities.fiscal_notification import FiscalNotification


class FiscalNotificationRepositoryProtocol(Protocol):
    """Persistence contract for fiscal notifications.

    Use cases depend on this abstraction, never on a concrete implementation.
    """

    async def get_by_part_number(self, part_number: str) -> Optional[FiscalNotification]:
        ...

    async def create(self, notification: FiscalNotification) -> FiscalNotification:
        ...
