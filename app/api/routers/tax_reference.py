from typing import List

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.tax_reference import (
    get_create_tax_reference_use_case,
    get_delete_tax_reference_use_case,
    get_get_tax_reference_by_order_use_case,
    get_get_tax_reference_by_product_use_case,
    get_get_tax_reference_use_case,
    get_list_tax_references_use_case,
    get_update_tax_reference_use_case,
)
from app.application.use_cases.tax_reference.use_cases import (
    CreateTaxReferenceUseCase,
    DeleteTaxReferenceUseCase,
    GetTaxReferenceByOrderUseCase,
    GetTaxReferenceByProductUseCase,
    GetTaxReferenceUseCase,
    ListTaxReferencesUseCase,
    UpdateTaxReferenceUseCase,
)
from app.schemas.tax_reference import (
    TaxReferenceCreate,
    TaxReferenceResponse,
    TaxReferenceUpdate,
)

router = APIRouter(prefix="/api/tax-reference", tags=["Tax Reference"])


@router.post(
    "/",
    response_model=TaxReferenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tax reference",
)
async def create_entry(
    data: TaxReferenceCreate,
    use_case: CreateTaxReferenceUseCase = Depends(get_create_tax_reference_use_case),
) -> TaxReferenceResponse:
    return await use_case.execute(data)


@router.get(
    "/product/{id_product}",
    response_model=List[TaxReferenceResponse],
    summary="List tax references by product",
)
async def get_by_product(
    id_product: int,
    use_case: GetTaxReferenceByProductUseCase = Depends(
        get_get_tax_reference_by_product_use_case
    ),
) -> List[TaxReferenceResponse]:
    return await use_case.execute(id_product)


@router.get(
    "/order/{vale_order_id}",
    response_model=List[TaxReferenceResponse],
    summary="List tax references by order",
)
async def get_by_order(
    vale_order_id: int,
    use_case: GetTaxReferenceByOrderUseCase = Depends(
        get_get_tax_reference_by_order_use_case
    ),
) -> List[TaxReferenceResponse]:
    return await use_case.execute(vale_order_id)


@router.get(
    "/",
    response_model=List[TaxReferenceResponse],
    summary="List all tax references",
)
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    use_case: ListTaxReferencesUseCase = Depends(get_list_tax_references_use_case),
) -> List[TaxReferenceResponse]:
    return await use_case.execute(skip, limit)


@router.get(
    "/{entry_id}",
    response_model=TaxReferenceResponse,
    summary="Get a tax reference by id",
)
async def get_by_id(
    entry_id: int,
    use_case: GetTaxReferenceUseCase = Depends(get_get_tax_reference_use_case),
) -> TaxReferenceResponse:
    return await use_case.execute(entry_id)


@router.patch(
    "/{entry_id}",
    response_model=TaxReferenceResponse,
    summary="Update a tax reference",
)
async def update_entry(
    entry_id: int,
    data: TaxReferenceUpdate,
    use_case: UpdateTaxReferenceUseCase = Depends(get_update_tax_reference_use_case),
) -> TaxReferenceResponse:
    return await use_case.execute(entry_id, data)


@router.delete("/{entry_id}", summary="Delete a tax reference")
async def delete_entry(
    entry_id: int,
    use_case: DeleteTaxReferenceUseCase = Depends(get_delete_tax_reference_use_case),
) -> dict:
    await use_case.execute(entry_id)
    return {"detail": f"Tax reference with ID {entry_id} deleted successfully"}
