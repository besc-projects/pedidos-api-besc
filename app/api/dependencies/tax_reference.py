from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.tax_reference.use_cases import (
    CreateTaxReferenceUseCase,
    DeleteTaxReferenceUseCase,
    GetTaxReferenceByOrderUseCase,
    GetTaxReferenceByProductUseCase,
    GetTaxReferenceUseCase,
    ListTaxReferencesUseCase,
    UpdateTaxReferenceUseCase,
)
from app.database import get_db
from app.domain.protocols.tax_reference_repository import (
    TaxReferenceRepositoryProtocol,
)
from app.infrastructure.repositories.tax_reference_repository import (
    SqlAlchemyTaxReferenceRepository,
)


def get_tax_reference_repository(
    db: AsyncSession = Depends(get_db),
) -> TaxReferenceRepositoryProtocol:
    return SqlAlchemyTaxReferenceRepository(db)


def get_create_tax_reference_use_case(
    repository: TaxReferenceRepositoryProtocol = Depends(get_tax_reference_repository),
) -> CreateTaxReferenceUseCase:
    return CreateTaxReferenceUseCase(repository)


def get_get_tax_reference_use_case(
    repository: TaxReferenceRepositoryProtocol = Depends(get_tax_reference_repository),
) -> GetTaxReferenceUseCase:
    return GetTaxReferenceUseCase(repository)


def get_get_tax_reference_by_product_use_case(
    repository: TaxReferenceRepositoryProtocol = Depends(get_tax_reference_repository),
) -> GetTaxReferenceByProductUseCase:
    return GetTaxReferenceByProductUseCase(repository)


def get_get_tax_reference_by_order_use_case(
    repository: TaxReferenceRepositoryProtocol = Depends(get_tax_reference_repository),
) -> GetTaxReferenceByOrderUseCase:
    return GetTaxReferenceByOrderUseCase(repository)


def get_list_tax_references_use_case(
    repository: TaxReferenceRepositoryProtocol = Depends(get_tax_reference_repository),
) -> ListTaxReferencesUseCase:
    return ListTaxReferencesUseCase(repository)


def get_update_tax_reference_use_case(
    repository: TaxReferenceRepositoryProtocol = Depends(get_tax_reference_repository),
) -> UpdateTaxReferenceUseCase:
    return UpdateTaxReferenceUseCase(repository)


def get_delete_tax_reference_use_case(
    repository: TaxReferenceRepositoryProtocol = Depends(get_tax_reference_repository),
) -> DeleteTaxReferenceUseCase:
    return DeleteTaxReferenceUseCase(repository)
