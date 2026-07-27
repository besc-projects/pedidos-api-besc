from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.price_table.use_cases import (
    CheckPnExistsUseCase,
    CreatePriceTableEntryUseCase,
    DeletePriceTableEntryUseCase,
    GetPriceByPnUseCase,
    GetPriceTableEntryUseCase,
    ListPriceTableEntriesUseCase,
    UpdatePriceTableEntryUseCase,
)
from app.database import get_db
from app.domain.protocols.price_table_repository import PriceTableRepositoryProtocol
from app.infrastructure.repositories.price_table_repository import (
    SqlAlchemyPriceTableRepository,
)


def get_price_table_repository(
    db: AsyncSession = Depends(get_db),
) -> PriceTableRepositoryProtocol:
    return SqlAlchemyPriceTableRepository(db)


def get_create_price_table_use_case(
    repository: PriceTableRepositoryProtocol = Depends(get_price_table_repository),
) -> CreatePriceTableEntryUseCase:
    return CreatePriceTableEntryUseCase(repository)


def get_get_price_table_use_case(
    repository: PriceTableRepositoryProtocol = Depends(get_price_table_repository),
) -> GetPriceTableEntryUseCase:
    return GetPriceTableEntryUseCase(repository)


def get_get_price_by_pn_use_case(
    repository: PriceTableRepositoryProtocol = Depends(get_price_table_repository),
) -> GetPriceByPnUseCase:
    return GetPriceByPnUseCase(repository)


def get_list_price_table_use_case(
    repository: PriceTableRepositoryProtocol = Depends(get_price_table_repository),
) -> ListPriceTableEntriesUseCase:
    return ListPriceTableEntriesUseCase(repository)


def get_update_price_table_use_case(
    repository: PriceTableRepositoryProtocol = Depends(get_price_table_repository),
) -> UpdatePriceTableEntryUseCase:
    return UpdatePriceTableEntryUseCase(repository)


def get_delete_price_table_use_case(
    repository: PriceTableRepositoryProtocol = Depends(get_price_table_repository),
) -> DeletePriceTableEntryUseCase:
    return DeletePriceTableEntryUseCase(repository)


def get_check_pn_exists_use_case(
    repository: PriceTableRepositoryProtocol = Depends(get_price_table_repository),
) -> CheckPnExistsUseCase:
    return CheckPnExistsUseCase(repository)
