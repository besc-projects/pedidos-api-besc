from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.fiscal_notifications.create_fiscal_notification import (
    CreateFiscalNotificationUseCase,
)
from app.application.use_cases.fiscal_notifications.get_fiscal_notification import (
    GetFiscalNotificationUseCase,
)
from app.database import get_db
from app.domain.protocols.fiscal_notification_repository import (
    FiscalNotificationRepositoryProtocol,
)
from app.infrastructure.repositories.fiscal_notification_repository import (
    SqlAlchemyFiscalNotificationRepository,
)


def get_fiscal_notification_repository(
    db: AsyncSession = Depends(get_db),
) -> FiscalNotificationRepositoryProtocol:
    """Provide the concrete repository behind its protocol."""
    return SqlAlchemyFiscalNotificationRepository(db)


def get_create_fiscal_notification_use_case(
    repository: FiscalNotificationRepositoryProtocol = Depends(
        get_fiscal_notification_repository
    ),
) -> CreateFiscalNotificationUseCase:
    return CreateFiscalNotificationUseCase(repository)


def get_get_fiscal_notification_use_case(
    repository: FiscalNotificationRepositoryProtocol = Depends(
        get_fiscal_notification_repository
    ),
) -> GetFiscalNotificationUseCase:
    return GetFiscalNotificationUseCase(repository)
