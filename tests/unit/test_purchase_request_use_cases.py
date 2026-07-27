import pytest

from app.application.use_cases.purchase_requests.create_purchase_request import (
    CreatePurchaseRequestUseCase,
)
from app.application.use_cases.purchase_requests.list_purchase_requests import (
    ListPurchaseRequestsUseCase,
)
from app.application.use_cases.purchase_requests.update_purchase_request import (
    UpdatePurchaseRequestUseCase,
)
from app.domain.enums.purchase_request_status import PurchaseRequestStatus
from app.domain.exceptions import (
    BusinessException,
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.schemas.purchase_requests import (
    PurchaseRequestCreate,
    PurchaseRequestFilter,
    PurchaseRequestUpdate,
)
from tests.fakes import FakePurchaseRequestRepository


def _create_payload(**overrides) -> PurchaseRequestCreate:
    data = {
        "orderId": 1,
        "productId": 10,
        "partNumber": "PN1",
        "releasedQuantity": 5,
        "requestedQuantity": 12,
    }
    data.update(overrides)
    return PurchaseRequestCreate.model_validate(data)


async def test_create_registers_pending_request():
    repository = FakePurchaseRequestRepository()
    use_case = CreatePurchaseRequestUseCase(repository)

    entity = await use_case.execute(_create_payload())

    assert entity.id == 1
    assert entity.status == PurchaseRequestStatus.PENDING


async def test_create_rejects_when_no_purchase_needed():
    repository = FakePurchaseRequestRepository()
    use_case = CreatePurchaseRequestUseCase(repository)

    with pytest.raises(BusinessException):
        await use_case.execute(_create_payload(releasedQuantity=12, requestedQuantity=12))


async def test_create_rejects_duplicate_order_and_part_number():
    repository = FakePurchaseRequestRepository()
    use_case = CreatePurchaseRequestUseCase(repository)

    await use_case.execute(_create_payload())
    with pytest.raises(ConflictException):
        await use_case.execute(_create_payload())


async def test_create_rejects_invalid_quantities():
    repository = FakePurchaseRequestRepository()
    use_case = CreatePurchaseRequestUseCase(repository)

    with pytest.raises(ValidationException):
        await use_case.execute(_create_payload(requestedQuantity=0))


async def test_update_recomputes_status_ignoring_client_status():
    repository = FakePurchaseRequestRepository()
    create = CreatePurchaseRequestUseCase(repository)
    created = await create.execute(_create_payload())

    update = UpdatePurchaseRequestUseCase(repository)
    updated = await update.execute(
        created.id,
        PurchaseRequestUpdate.model_validate(
            {"releasedQuantity": 15, "status": "PENDING"}
        ),
    )

    assert updated.status == PurchaseRequestStatus.COMPLETED


async def test_update_raises_not_found():
    repository = FakePurchaseRequestRepository()
    use_case = UpdatePurchaseRequestUseCase(repository)

    with pytest.raises(NotFoundException):
        await use_case.execute(
            999, PurchaseRequestUpdate.model_validate({"releasedQuantity": 1})
        )


async def test_update_raises_when_no_fields():
    repository = FakePurchaseRequestRepository()
    create = CreatePurchaseRequestUseCase(repository)
    created = await create.execute(_create_payload())

    update = UpdatePurchaseRequestUseCase(repository)
    with pytest.raises(ValidationException):
        await update.execute(created.id, PurchaseRequestUpdate())


async def test_list_filters_by_status():
    repository = FakePurchaseRequestRepository()
    create = CreatePurchaseRequestUseCase(repository)
    await create.execute(_create_payload(partNumber="PN1"))
    await create.execute(_create_payload(partNumber="PN2"))

    list_use_case = ListPurchaseRequestsUseCase(repository)
    pending = await list_use_case.execute(
        PurchaseRequestFilter(order_id=1, status=PurchaseRequestStatus.PENDING)
    )
    completed = await list_use_case.execute(
        PurchaseRequestFilter(order_id=1, status=PurchaseRequestStatus.COMPLETED)
    )

    assert len(pending) == 2
    assert len(completed) == 0
