"""Integration tests for the auth/users endpoints (ephemeral SQLite)."""


async def test_register_and_login_flow(client):
    register = await client.post(
        "/api/users/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secret",
            "company": "acme",
        },
    )
    assert register.status_code == 201
    assert register.json()["user"]["username"] == "alice"

    duplicate = await client.post(
        "/api/users/register",
        json={
            "username": "alice",
            "email": "alice2@example.com",
            "password": "secret",
            "company": "acme",
        },
    )
    assert duplicate.status_code == 409

    login = await client.post(
        "/api/users/login",
        json={"username": "alice", "password": "secret"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


async def test_login_invalid_credentials(client):
    response = await client.post(
        "/api/users/login",
        json={"username": "ghost", "password": "nope"},
    )
    assert response.status_code == 401
