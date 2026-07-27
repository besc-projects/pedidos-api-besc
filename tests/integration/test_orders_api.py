"""Integration tests for the orders endpoints (ephemeral SQLite)."""

VALE_ORDER_ID = 6600001


def _order_payload(**overrides) -> dict:
    data = {
        "vale_order_id": VALE_ORDER_ID,
        "total_value": 250.0,
        "cnpj": "00000000000000",
        "portal": "portal",
        "center": "center",
        "state": "MG",
        "date": "2026-01-01T00:00:00",
    }
    data.update(overrides)
    return data


async def test_order_lifecycle(client):
    created = await client.post("/api/orders/", json=_order_payload())
    assert created.status_code == 201
    assert created.json()["order"]["process_id"] == 1

    fetched = await client.get(f"/api/orders/get_order/{VALE_ORDER_ID}")
    assert fetched.status_code == 200
    assert fetched.json()["order"]["vale_order_id"] == VALE_ORDER_ID

    pending = await client.get("/api/orders/pending")
    assert pending.status_code == 200
    assert pending.json()["total"] == 1

    status_update = await client.put(
        f"/api/orders/status/{VALE_ORDER_ID}",
        json={"process_id": 2, "status_code": 1},
    )
    assert status_update.status_code == 200
    assert status_update.json()["order"]["process_id"] == 2

    patched = await client.patch(
        f"/api/orders/{VALE_ORDER_ID}", json={"portal": "new-portal"}
    )
    assert patched.status_code == 200
    assert "portal" in patched.json()["updated_fields"]

    by_status = await client.get("/api/orders/status?process_id=2&status_code=1")
    assert by_status.status_code == 200
    assert by_status.json()["total"] == 1


async def test_get_missing_order_returns_404(client):
    response = await client.get("/api/orders/get_order/99999999")
    assert response.status_code == 404


async def test_patch_missing_order_returns_404(client):
    response = await client.patch("/api/orders/99999999", json={"portal": "x"})
    assert response.status_code == 404
