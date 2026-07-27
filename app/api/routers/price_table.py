from typing import List

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.price_table import (
    get_check_pn_exists_use_case,
    get_create_price_table_use_case,
    get_delete_price_table_use_case,
    get_get_price_by_pn_use_case,
    get_get_price_table_use_case,
    get_list_price_table_use_case,
    get_update_price_table_use_case,
)
from app.application.use_cases.price_table.use_cases import (
    CheckPnExistsUseCase,
    CreatePriceTableEntryUseCase,
    DeletePriceTableEntryUseCase,
    GetPriceByPnUseCase,
    GetPriceTableEntryUseCase,
    ListPriceTableEntriesUseCase,
    UpdatePriceTableEntryUseCase,
)
from app.schemas.price_table import (
    PriceByPNResponse,
    PriceTableCreate,
    PriceTableResponse,
    PriceTableUpdate,
)

router = APIRouter(prefix="/api/price-table", tags=["Price Table"])


@router.post(
    "/",
    response_model=PriceTableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a price-table entry",
)
async def create_price_entry(
    price_data: PriceTableCreate,
    use_case: CreatePriceTableEntryUseCase = Depends(get_create_price_table_use_case),
) -> PriceTableResponse:
    return await use_case.execute(price_data)


@router.get(
    "/price/{pn}",
    response_model=PriceByPNResponse,
    summary="Get unit price by PN and state",
)
async def get_price_for_pn(
    pn: str,
    state: str = Query(..., min_length=2, max_length=2),
    use_case: GetPriceByPnUseCase = Depends(get_get_price_by_pn_use_case),
) -> PriceByPNResponse:
    entry = await use_case.execute(pn, state)
    return PriceByPNResponse(
        pn=entry.pn,
        unit_price=entry.unit_price,
        description=entry.description,
        destination=entry.destination,
    )


@router.get("/{entry_id}", response_model=PriceTableResponse, summary="Get entry by id")
async def get_entry_by_id(
    entry_id: int,
    use_case: GetPriceTableEntryUseCase = Depends(get_get_price_table_use_case),
) -> PriceTableResponse:
    return await use_case.execute(entry_id)


@router.get(
    "/",
    response_model=List[PriceTableResponse],
    summary="List price-table entries",
)
async def get_all_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    use_case: ListPriceTableEntriesUseCase = Depends(get_list_price_table_use_case),
) -> List[PriceTableResponse]:
    return await use_case.execute(skip, limit)


@router.patch(
    "/{entry_id}",
    response_model=PriceTableResponse,
    summary="Update a price-table entry",
)
async def update_entry(
    entry_id: int,
    price_data: PriceTableUpdate,
    use_case: UpdatePriceTableEntryUseCase = Depends(get_update_price_table_use_case),
) -> PriceTableResponse:
    return await use_case.execute(entry_id, price_data)


@router.delete("/{entry_id}", summary="Delete a price-table entry")
async def delete_entry(
    entry_id: int,
    use_case: DeletePriceTableEntryUseCase = Depends(get_delete_price_table_use_case),
) -> dict:
    await use_case.execute(entry_id)
    return {"message": f"Price table entry with ID {entry_id} deleted successfully"}


@router.get("/check/{pn}", summary="Check whether a PN exists for a state")
async def check_pn(
    pn: str,
    state: str = Query(..., min_length=2, max_length=2),
    use_case: CheckPnExistsUseCase = Depends(get_check_pn_exists_use_case),
) -> dict:
    exists = await use_case.execute(pn, state)
    return {"pn": pn, "state": state.upper(), "exists": exists}
