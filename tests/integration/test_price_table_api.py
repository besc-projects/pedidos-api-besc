"""Integration tests for the price-table endpoints (ephemeral SQLite)."""


async def test_full_price_table_flow(client):
    create = await client.post(
        "/api/price-table/",
        json={
            "pn": "PN-TEST",
            "long_description": "Long description",
            "description": "Short",
            "destination": "mg",
            "unit_price": 42.5,
        },
    )
    assert create.status_code == 201
    body = create.json()
    assert body["destination"] == "MG"
    entry_id = body["id"]

    duplicate = await client.post(
        "/api/price-table/",
        json={
            "pn": "PN-TEST",
            "long_description": "x",
            "description": "y",
            "destination": "MG",
            "unit_price": 1.0,
        },
    )
    assert duplicate.status_code == 409

    price = await client.get("/api/price-table/price/PN-TEST?state=mg")
    assert price.status_code == 200
    assert price.json()["unit_price"] == 42.5

    fetched = await client.get(f"/api/price-table/{entry_id}")
    assert fetched.status_code == 200

    listing = await client.get("/api/price-table/")
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    updated = await client.patch(
        f"/api/price-table/{entry_id}", json={"unit_price": 99.9}
    )
    assert updated.status_code == 200
    assert updated.json()["unit_price"] == 99.9

    check = await client.get("/api/price-table/check/PN-TEST?state=mg")
    assert check.json()["exists"] is True

    deleted = await client.delete(f"/api/price-table/{entry_id}")
    assert deleted.status_code == 200


async def test_get_missing_entry_returns_404(client):
    response = await client.get("/api/price-table/99999")
    assert response.status_code == 404
