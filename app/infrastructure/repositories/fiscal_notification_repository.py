from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.fiscal_notification import FiscalNotification
from app.models.fiscal_notifications import FiscalNotification as FiscalNotificationModel


class SqlAlchemyFiscalNotificationRepository:
    """SQLAlchemy implementation of the fiscal-notification persistence contract."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: FiscalNotificationModel) -> FiscalNotification:
        return FiscalNotification(
            id=model.id,
            part_number=model.part_number,
            vale_order_id=model.vale_order_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_part_number(self, part_number: str) -> Optional[FiscalNotification]:
        result = await self._session.execute(
            select(FiscalNotificationModel).where(
                FiscalNotificationModel.part_number == part_number
            )
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def create(self, notification: FiscalNotification) -> FiscalNotification:
        model = FiscalNotificationModel(
            part_number=notification.part_number,
            vale_order_id=notification.vale_order_id,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)
