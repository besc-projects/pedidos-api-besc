"""Integration tests for the tickets endpoints (ephemeral SQLite)."""

from datetime import datetime

from app.models.orders import Order as OrderModel

PURCHASE_ORDER = 7700001
TICKET_NUMBER = 4242


async def _seed_order(db_session) -> int:
    order = OrderModel(
        vale_order_id=PURCHASE_ORDER,
        total_value=100,
        cnpj="00000000000000",
        date=datetime(2026, 1, 1),
    )
    db_session.add(order)
    await db_session.flush()
    return order.id


async def test_ticket_lifecycle(client, db_session):
    await _seed_order(db_session)

    created = await client.post(
        "/api/tickets/",
        json={
            "ticket_number": TICKET_NUMBER,
            "purchase_order": PURCHASE_ORDER,
            "status_id": 0,
        },
    )
    assert created.status_code == 201
    ticket_id = created.json()["id"]

    duplicate = await client.post(
        "/api/tickets/",
        json={
            "ticket_number": TICKET_NUMBER,
            "purchase_order": PURCHASE_ORDER,
            "status_id": 0,
        },
    )
    assert duplicate.status_code == 409

    fetched = await client.get(f"/api/tickets/{TICKET_NUMBER}")
    assert fetched.status_code == 200

    updated = await client.patch(
        f"/api/tickets/{ticket_id}", json={"status_id": 2}
    )
    assert updated.status_code == 200
    body = updated.json()
    assert "status_id" in body["updated_fields"]
    assert "observer_range_date" in body["updated_fields"]

    deleted = await client.delete(f"/api/tickets/{ticket_id}")
    assert deleted.status_code == 200


async def test_ticket_progress_and_divergence(client, db_session):
    await _seed_order(db_session)
    created = await client.post(
        "/api/tickets/",
        json={
            "ticket_number": TICKET_NUMBER,
            "purchase_order": PURCHASE_ORDER,
            "status_id": 0,
        },
    )
    ticket_id = created.json()["id"]

    progress = await client.post(
        f"/api/{ticket_id}/progresses/",
        json={"status_progress_id": 1},
    )
    assert progress.status_code == 201

    progresses = await client.get(f"/api/{ticket_id}/progresses/")
    assert progresses.status_code == 200
    assert len(progresses.json()) == 1

    divergence = await client.post(
        f"/api/{ticket_id}/divergences/",
        json={"purchase_order_line": 1, "item_id": 10, "taxes": "x"},
    )
    assert divergence.status_code == 201

    duplicate = await client.post(
        f"/api/{ticket_id}/divergences/",
        json={"purchase_order_line": 1, "item_id": 10},
    )
    assert duplicate.status_code == 409

    item_ids = await client.get(f"/api/tickets/{TICKET_NUMBER}/divergences/items")
    assert item_ids.status_code == 200
    assert item_ids.json() == [10]


async def test_create_ticket_unknown_order_returns_404(client):
    response = await client.post(
        "/api/tickets/",
        json={"ticket_number": 1, "purchase_order": 99999999, "status_id": 0},
    )
    assert response.status_code == 404
