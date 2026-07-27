"""Integration tests for the products endpoints (ephemeral SQLite)."""

from datetime import datetime

from app.models.orders import Order as OrderModel

TEST_VALE_ORDER_ID = 8800001


async def _seed_order(db_session) -> int:
    order = OrderModel(
        vale_order_id=TEST_VALE_ORDER_ID,
        total_value=100,
        cnpj="00000000000000",
        date=datetime(2026, 1, 1),
    )
    db_session.add(order)
    await db_session.flush()
    return order.id


async def test_bulk_create_and_list_products(client, db_session):
    internal_id = await _seed_order(db_session)

    created = await client.post(
        f"/api/products/bulk/order/{TEST_VALE_ORDER_ID}",
        json=[
            {"part_number": "PN1", "description": "first", "quantity": 2},
            {"part_number": "PN2", "description": "second", "quantity": 5},
        ],
    )
    assert created.status_code == 201
    assert len(created.json()) == 2
    product_id = created.json()[0]["id"]

    listing = await client.get(f"/api/products/order/{internal_id}")
    assert listing.status_code == 200
    assert len(listing.json()) == 2

    fetched = await client.get(f"/api/products/{product_id}")
    assert fetched.status_code == 200

    updated = await client.put(
        f"/api/products/{product_id}", json={"description": "updated"}
    )
    assert updated.status_code == 200
    assert updated.json()["description"] == "updated"


async def test_bulk_create_unknown_order_returns_404(client):
    response = await client.post(
        "/api/products/bulk/order/99999999",
        json=[{"part_number": "PN1"}],
    )
    assert response.status_code == 404


async def test_get_missing_product_returns_404(client):
    response = await client.get("/api/products/99999999")
    assert response.status_code == 404
