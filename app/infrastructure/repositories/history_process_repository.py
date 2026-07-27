from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.history_process_entry import HistoryProcessEntry
from app.models.history_process import HistoryProcess as HistoryProcessModel


class SqlAlchemyHistoryProcessRepository:
    """SQLAlchemy persistence for process-history events."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: HistoryProcessModel) -> HistoryProcessEntry:
        return HistoryProcessEntry(
            id=model.id,
            order_id=model.order_id,
            step=model.step,
            description=model.description,
            severity=model.severity,
            created_by=model.created_by,
            occurred_at=model.occurred_at,
            created_at=model.created_at,
        )

    async def get_by_order_and_description(
        self, order_id: int, description: str
    ) -> Optional[HistoryProcessEntry]:
        result = await self._session.execute(
            select(HistoryProcessModel).where(
                HistoryProcessModel.order_id == order_id,
                HistoryProcessModel.description == description,
            )
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(HistoryProcessModel)
        )
        return int(result.scalar_one())

    async def list(self, skip: int, limit: int) -> list[HistoryProcessEntry]:
        result = await self._session.execute(
            select(HistoryProcessModel)
            .order_by(HistoryProcessModel.occurred_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_by_order(self, order_id: int) -> list[HistoryProcessEntry]:
        result = await self._session.execute(
            select(HistoryProcessModel)
            .where(HistoryProcessModel.order_id == order_id)
            .order_by(HistoryProcessModel.occurred_at.desc())
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_by_step(
        self, order_id: int, step: str
    ) -> list[HistoryProcessEntry]:
        result = await self._session.execute(
            select(HistoryProcessModel)
            .where(
                HistoryProcessModel.order_id == order_id,
                HistoryProcessModel.step == step,
            )
            .order_by(HistoryProcessModel.occurred_at.desc())
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def create(self, entry: HistoryProcessEntry) -> HistoryProcessEntry:
        values = {
            "order_id": entry.order_id,
            "step": entry.step,
            "description": entry.description,
            "severity": entry.severity,
            "created_by": entry.created_by,
        }
        if entry.occurred_at is not None:
            values["occurred_at"] = entry.occurred_at

        model = HistoryProcessModel(**values)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)
