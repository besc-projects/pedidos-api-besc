"""Integration tests for the purchase-requests endpoints.

They exercise the real HTTP stack and database; every write is reverted by the
rolled-back transaction provided by the ``client`` fixture.
"""

TEST_ORDER_ID = 990001


async def test_create_list_and_update_flow(client):
    create_response = await client.post(
        "/api/purchase-requests/",
        json={
            "orderId": TEST_ORDER_ID,
            "productId": 20,
            "supplierProductCode": "00038",
            "partNumber": "PMN1SX",
            "releasedQuantity": 5,
            "requestedQuantity": 12,
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()["purchase_request"]
    assert created["status"] == "PENDING"
    purchase_request_id = created["id"]

    duplicate_response = await client.post(
        "/api/purchase-requests/",
        json={
            "orderId": TEST_ORDER_ID,
            "productId": 20,
            "partNumber": "PMN1SX",
            "releasedQuantity": 5,
            "requestedQuantity": 12,
        },
    )
    assert duplicate_response.status_code == 409

    list_response = await client.get(f"/api/purchase-requests/?orderId={TEST_ORDER_ID}")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    update_response = await client.put(
        f"/api/purchase-requests/{purchase_request_id}",
        json={"releasedQuantity": 15, "status": "PENDING"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["purchase_request"]["status"] == "COMPLETED"


async def test_create_rejects_when_no_purchase_needed(client):
    response = await client.post(
        "/api/purchase-requests/",
        json={
            "orderId": TEST_ORDER_ID,
            "productId": 21,
            "partNumber": "SUF001",
            "releasedQuantity": 10,
            "requestedQuantity": 10,
        },
    )
    assert response.status_code == 400


async def test_update_missing_returns_404(client):
    response = await client.put(
        "/api/purchase-requests/99999999",
        json={"releasedQuantity": 1},
    )
    assert response.status_code == 404
