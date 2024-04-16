from typing import AsyncIterable

import httpx
import pytest
import pytest_asyncio

from app.main.web import create_app


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncIterable[httpx.AsyncClient]:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture(scope="session")
def post_user_data() -> dict:
    return {"username": "alim", "password": "superpassword"}


@pytest_asyncio.fixture(scope="session")
async def auth_cookies(client: httpx.AsyncClient, post_user_data: dict) -> dict:
    response = await client.post(
        "/auth/login",
        data=post_user_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    return {"access_token": response.cookies.get("access_token")}


@pytest.mark.asyncio
async def test_register_user(client: httpx.AsyncClient, post_user_data: dict) -> None:
    response = await client.post("/auth/register", json=post_user_data)

    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": "alim"}


@pytest.mark.asyncio
async def test_register_user_already_exists(
    client: httpx.AsyncClient, post_user_data: dict
) -> None:
    response = await client.post("/auth/register", json=post_user_data)

    assert response.status_code == 409
    assert response.json() == {"detail": "User already exists"}


@pytest.mark.asyncio
async def test_get_authenticated_user(
    client: httpx.AsyncClient, auth_cookies: dict
) -> None:
    response = await client.get("/auth/me", cookies=auth_cookies)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "alim"}


@pytest.mark.asyncio
async def test_delete_authenticated_user(
    client: httpx.AsyncClient, auth_cookies: dict
) -> None:
    response = await client.delete("/auth/me", cookies=auth_cookies)

    assert response.status_code == 204
    assert not response.content
