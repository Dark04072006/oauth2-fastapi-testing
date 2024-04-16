from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import UserAlreadyExists, UserIsNotAuthenticated


async def user_is_not_authenticated(
    request: Request, exc: UserIsNotAuthenticated
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def user_already_exists(request: Request, exc: UserAlreadyExists) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})
