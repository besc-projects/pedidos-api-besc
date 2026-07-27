import pytest

from app.domain.entities.purchase_request import PurchaseRequest
from app.domain.enums.purchase_request_status import PurchaseRequestStatus
from app.domain.exceptions import ValidationException


def _build(released: float, requested: float) -> PurchaseRequest:
    return PurchaseRequest(
        order_id=1,
        product_id=1,
        part_number="PN1",
        released_quantity=released,
        requested_quantity=requested,
    )


def test_status_is_pending_when_released_below_requested():
    entity = _build(released=5, requested=12)
    assert entity.status == PurchaseRequestStatus.PENDING
    assert entity.needs_purchase() is True


def test_status_is_completed_when_released_meets_requested():
    entity = _build(released=12, requested=12)
    assert entity.status == PurchaseRequestStatus.COMPLETED
    assert entity.needs_purchase() is False


def test_requested_quantity_must_be_greater_than_zero():
    with pytest.raises(ValidationException):
        _build(released=1, requested=0)


def test_released_quantity_cannot_be_negative():
    with pytest.raises(ValidationException):
        _build(released=-1, requested=5)


def test_change_quantities_recomputes_status_to_completed():
    entity = _build(released=5, requested=12)
    entity.change_quantities(released_quantity=15)
    assert entity.status == PurchaseRequestStatus.COMPLETED


def test_change_quantities_keeps_rule_over_manual_intent():
    entity = _build(released=5, requested=12)
    entity.change_quantities(requested_quantity=4)
    assert entity.status == PurchaseRequestStatus.COMPLETED
