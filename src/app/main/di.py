from functools import wraps
from typing import Annotated, Callable, ParamSpec, TypeVar

from fastapi import Depends, FastAPI, Request

from app.adapters.auth.token import JwtTokenOptions, JwtTokenProcessor, TokenIdProvider
from app.adapters.data.repository import UserRepository
from app.api.stub import Stub
from app.use_cases.users import (
    DeleteAuthenticatedUser,
    GetAuthenticatedUser,
    LoginUser,
    RegisterUser,
)

DecoratedSingletonT = TypeVar("DecoratedSingletonT")
DecoratedParamSpec = ParamSpec("DecoratedParamSpec")


def singleton_decorator(func: Callable) -> DecoratedSingletonT:
    """
    Decorator that creates a singleton instance of the decorated function.
    """

    instances = {}

    @wraps(func)
    def wrapper(
        *args: DecoratedParamSpec.args, **kwargs: DecoratedParamSpec.kwargs
    ) -> DecoratedSingletonT:
        if func not in instances:
            instances[func] = func(*args, **kwargs)
        return instances[func]

    return wrapper


@singleton_decorator
def provide_jwt_options() -> JwtTokenOptions:
    return JwtTokenOptions.from_env()


@singleton_decorator
def provide_jwt_processor(
    options: Annotated[JwtTokenOptions, Depends(Stub(JwtTokenOptions))],
) -> JwtTokenProcessor:
    return JwtTokenProcessor(options)


def provide_id_provider(
    request: Request,
    token_processor: Annotated[JwtTokenProcessor, Depends(Stub(JwtTokenProcessor))],
) -> TokenIdProvider:
    return TokenIdProvider(token_processor, request.auth)


@singleton_decorator
def provide_user_repository() -> UserRepository:
    return UserRepository()


def provide_login_user_interactor(
    user_repository: Annotated[UserRepository, Depends(Stub(UserRepository))],
) -> LoginUser:
    return LoginUser(user_repository)


def provide_register_user_interactor(
    user_repository: Annotated[UserRepository, Depends(Stub(UserRepository))],
) -> RegisterUser:
    return RegisterUser(user_repository)


def provide_get_authenticated_user_interactor(
    id_provider: Annotated[TokenIdProvider, Depends(Stub(TokenIdProvider))],
    user_repository: Annotated[UserRepository, Depends(Stub(UserRepository))],
) -> GetAuthenticatedUser:
    return GetAuthenticatedUser(id_provider, user_repository)


def provide_delete_authenticated_user_interactor(
    id_provider: Annotated[TokenIdProvider, Depends(Stub(TokenIdProvider))],
    user_repository: Annotated[UserRepository, Depends(Stub(UserRepository))],
) -> DeleteAuthenticatedUser:
    return DeleteAuthenticatedUser(id_provider, user_repository)


def init_dependencies_fastapi(app: FastAPI) -> None:
    app.dependency_overrides.update(
        {
            JwtTokenOptions: provide_jwt_options,
            JwtTokenProcessor: provide_jwt_processor,
            TokenIdProvider: provide_id_provider,
            UserRepository: provide_user_repository,
            LoginUser: provide_login_user_interactor,
            RegisterUser: provide_register_user_interactor,
            GetAuthenticatedUser: provide_get_authenticated_user_interactor,
            DeleteAuthenticatedUser: provide_delete_authenticated_user_interactor,
        }
    )
