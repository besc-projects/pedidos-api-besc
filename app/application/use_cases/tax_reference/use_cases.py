from __future__ import annotations

from app.domain.entities.tax_reference import TaxReference
from app.domain.exceptions import NotFoundException
from app.domain.protocols.tax_reference_repository import (
    TaxReferenceRepositoryProtocol,
)
from app.schemas.tax_reference import TaxReferenceCreate, TaxReferenceUpdate


class CreateTaxReferenceUseCase:
    """Create a product tax reference."""

    def __init__(self, repository: TaxReferenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: TaxReferenceCreate) -> TaxReference:
        tax_reference = TaxReference(
            id_product=data.id_product,
            ncm_code=data.ncm_code,
            ipi=data.ipi,
            icms=data.icms,
            icms_st=data.icms_st,
            origin=data.origin,
        )
        return await self._repository.create(tax_reference)


class GetTaxReferenceUseCase:
    """Retrieve a tax reference by id."""

    def __init__(self, repository: TaxReferenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, entry_id: int) -> TaxReference:
        entry = await self._repository.get_by_id(entry_id)
        if entry is None:
            raise NotFoundException(f"Tax reference with ID {entry_id} not found.")
        return entry


class GetTaxReferenceByProductUseCase:
    """List tax references for a product."""

    def __init__(self, repository: TaxReferenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, id_product: int) -> list[TaxReference]:
        entries = await self._repository.list_by_product(id_product)
        if not entries:
            raise NotFoundException(
                f"No tax reference found for product {id_product}."
            )
        return entries


class GetTaxReferenceByOrderUseCase:
    """List tax references linked to an order's products."""

    def __init__(self, repository: TaxReferenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, vale_order_id: int) -> list[TaxReference]:
        entries = await self._repository.list_by_order(vale_order_id)
        if not entries:
            raise NotFoundException(
                f"No tax reference found for order {vale_order_id}."
            )
        return entries


class ListTaxReferencesUseCase:
    """List tax references with pagination."""

    def __init__(self, repository: TaxReferenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, skip: int, limit: int) -> list[TaxReference]:
        return await self._repository.list(skip, limit)


class UpdateTaxReferenceUseCase:
    """Apply a partial update to a tax reference."""

    def __init__(self, repository: TaxReferenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, entry_id: int, data: TaxReferenceUpdate) -> TaxReference:
        entry = await self._repository.get_by_id(entry_id)
        if entry is None:
            raise NotFoundException(f"Tax reference with ID {entry_id} not found.")
        changes = data.model_dump(exclude_unset=True)
        return await self._repository.update(entry, changes)


class DeleteTaxReferenceUseCase:
    """Delete a tax reference by id."""

    def __init__(self, repository: TaxReferenceRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, entry_id: int) -> None:
        deleted = await self._repository.delete(entry_id)
        if not deleted:
            raise NotFoundException(f"Tax reference with ID {entry_id} not found.")
