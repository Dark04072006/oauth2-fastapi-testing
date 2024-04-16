from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.adapters.auth.token import JwtTokenProcessor
from app.api.dependencies.authentication import auth_required
from app.api.stub import Stub
from app.use_cases.users import (
    DeleteAuthenticatedUser,
    GetAuthenticatedUser,
    LoginUser,
    RegisterUser,
)

auth_router = APIRouter(prefix="/auth", tags=["authentication"])


@dataclass(frozen=True)
class UserPostSchema:
    username: str
    password: str


@dataclass(frozen=True)
class UserSchema:
    id: int
    username: str


@auth_router.post("/login", response_model=UserSchema)
def login_for_access_token(
    schema: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    interactor: Annotated[LoginUser, Depends(Stub(LoginUser))],
    token_processor: Annotated[JwtTokenProcessor, Depends(Stub(JwtTokenProcessor))],
) -> UserSchema:
    user = interactor.execute(schema.username, schema.password)

    token = token_processor.generate_token(user.id)

    response.set_cookie("access_token", f"Bearer {token}", httponly=True)

    return UserSchema(id=user.id, username=user.username)


@auth_router.post("/register", response_model=UserSchema, status_code=201)
def register_user(
    schema: UserPostSchema,
    interactor: Annotated[RegisterUser, Depends(Stub(RegisterUser))],
) -> UserSchema:
    user = interactor.execute(schema.username, schema.password)

    return UserSchema(id=user.id, username=user.username)


@auth_router.get(
    "/me",
    response_model=UserSchema,
    dependencies=[Depends(auth_required)],
)
def get_authenticated_user(
    interactor: Annotated[GetAuthenticatedUser, Depends(Stub(GetAuthenticatedUser))],
) -> UserSchema:
    user = interactor.execute()

    return UserSchema(id=user.id, username=user.username)


@auth_router.delete(
    "/me",
    status_code=204,
    dependencies=[Depends(auth_required)],
    response_model=None,
    response_description="User deleted",
)
def delete_authenticated_user(
    interactor: Annotated[
        DeleteAuthenticatedUser, Depends(Stub(DeleteAuthenticatedUser))
    ],
) -> None:
    interactor.execute()
