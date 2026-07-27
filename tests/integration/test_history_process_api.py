"""Integration tests for the history-process endpoints (ephemeral SQLite)."""


async def test_create_and_list_flow(client):
    create = await client.post(
        "/api/history-process/",
        json={
            "order_id": 12345,
            "step": "cadastro",
            "description": "Order created",
            "severity": "info",
        },
    )
    assert create.status_code == 201

    duplicate = await client.post(
        "/api/history-process/",
        json={
            "order_id": 12345,
            "step": "cadastro",
            "description": "Order created",
        },
    )
    assert duplicate.status_code == 409

    listing = await client.get("/api/history-process/")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1

    by_order = await client.get("/api/history-process/order/12345")
    assert by_order.status_code == 200
    assert by_order.json()["total"] == 1

    by_step = await client.get("/api/history-process/order/12345/step/cadastro")
    assert by_step.status_code == 200


async def test_list_by_order_not_found(client):
    response = await client.get("/api/history-process/order/99999999")
    assert response.status_code == 404
