"""Integration tests for the tax-reference endpoints (ephemeral SQLite)."""


async def test_full_tax_reference_flow(client):
    create = await client.post(
        "/api/tax-reference/",
        json={
            "id_product": 555,
            "ncm_code": "1234567890",
            "ipi": 5.0,
            "icms": 12.0,
            "origin": "0",
        },
    )
    assert create.status_code == 201
    entry_id = create.json()["id"]

    by_product = await client.get("/api/tax-reference/product/555")
    assert by_product.status_code == 200
    assert len(by_product.json()) == 1

    fetched = await client.get(f"/api/tax-reference/{entry_id}")
    assert fetched.status_code == 200

    listing = await client.get("/api/tax-reference/")
    assert listing.status_code == 200

    updated = await client.patch(
        f"/api/tax-reference/{entry_id}", json={"ncm_code": "9999999999"}
    )
    assert updated.status_code == 200
    assert updated.json()["ncm_code"] == "9999999999"

    deleted = await client.delete(f"/api/tax-reference/{entry_id}")
    assert deleted.status_code == 200


async def test_get_missing_returns_404(client):
    response = await client.get("/api/tax-reference/99999")
    assert response.status_code == 404
