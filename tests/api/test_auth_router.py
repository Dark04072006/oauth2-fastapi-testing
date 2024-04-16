from typing import AsyncIterable

import httpx
import pytest
import pytest_asyncio

from app.main.web import create_app


@pytest_asyncio.fixture
async def client() -> AsyncIterable[httpx.AsyncClient]:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client


COOKIES = dict()
POST_USER_DATA = {"username": "alim", "password": "superpassword"}


@pytest.mark.asyncio
async def test_register_user(client: httpx.AsyncClient) -> None:
    response = await client.post("/auth/register", json=POST_USER_DATA)

    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": "alim"}


@pytest.mark.asyncio
async def test_register_user_already_exists(client: httpx.AsyncClient) -> None:
    response = await client.post("/auth/register", json=POST_USER_DATA)

    assert response.status_code == 409
    assert response.json() == {"detail": "User already exists"}


@pytest.mark.asyncio
async def test_login_user(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        data=POST_USER_DATA,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "alim"}
    assert "access_token" in response.cookies

    COOKIES.update({"access_token": response.cookies.get("access_token")})


@pytest.mark.asyncio
async def test_get_authenticated_user(client: httpx.AsyncClient) -> None:
    response = await client.get("/auth/me", cookies=COOKIES)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "alim"}


@pytest.mark.asyncio
async def test_delete_authenticated_user(client: httpx.AsyncClient) -> None:
    response = await client.delete("/auth/me", cookies=COOKIES)

    assert response.status_code == 204
    assert not response.content
