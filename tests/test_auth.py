import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_register_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data

async def test_register_duplicate_user(async_client: AsyncClient):
    # Register first
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "test2@example.com", "password": "securepassword"}
    )
    # Register duplicate
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "test2@example.com", "password": "securepassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "A user with this email already exists."

async def test_login_user(async_client: AsyncClient):
    # Register first
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "test_login@example.com", "password": "securepassword"}
    )
    
    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "test_login@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_invalid_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@example.com", "password": "securepassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"
