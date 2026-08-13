from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.price_table_entry import PriceTableEntry
from app.models.price_table import PriceTable as PriceTableModel


class SqlAlchemyPriceTableRepository:
    """SQLAlchemy persistence for price-table entries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: PriceTableModel) -> PriceTableEntry:
        return PriceTableEntry(
            id=model.id,
            pn=model.pn,
            long_description=model.long_description,
            description=model.description,
            destination=model.destination,
            unit_price=model.unit_price,
        )

    async def get_by_id(self, entry_id: int) -> Optional[PriceTableEntry]:
        result = await self._session.execute(
            select(PriceTableModel).where(PriceTableModel.id == entry_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_pn_and_destination(
        self, pn: str, destination: str
    ) -> Optional[PriceTableEntry]:
        result = await self._session.execute(
            select(PriceTableModel).where(
                PriceTableModel.pn == pn,
                PriceTableModel.destination == destination,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(self, skip: int, limit: int) -> list[PriceTableEntry]:
        result = await self._session.execute(
            select(PriceTableModel)
            .order_by(PriceTableModel.id)
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def create(self, entry: PriceTableEntry) -> PriceTableEntry:
        model = PriceTableModel(
            pn=entry.pn,
            long_description=entry.long_description,
            description=entry.description,
            destination=entry.destination,
            unit_price=entry.unit_price,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(
        self, entry: PriceTableEntry, changes: dict
    ) -> PriceTableEntry:
        result = await self._session.execute(
            select(PriceTableModel).where(PriceTableModel.id == entry.id)
        )
        model = result.scalar_one_or_none()
        for field, value in changes.items():
            setattr(model, field, value)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, entry_id: int) -> bool:
        result = await self._session.execute(
            select(PriceTableModel).where(PriceTableModel.id == entry_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
