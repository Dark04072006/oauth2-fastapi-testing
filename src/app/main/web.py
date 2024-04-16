from fastapi import FastAPI

from app.api.exc_handlers import user_already_exists, user_is_not_authenticated
from app.api.router.auth import auth_router
from app.domain.exceptions import UserAlreadyExists, UserIsNotAuthenticated
from app.main.di import init_dependencies_fastapi


def init_routers(app: FastAPI) -> None:
    app.include_router(auth_router)


def init_exc_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserIsNotAuthenticated, user_is_not_authenticated)
    app.add_exception_handler(UserAlreadyExists, user_already_exists)


def create_app() -> FastAPI:
    app = FastAPI()

    init_dependencies_fastapi(app)
    init_routers(app)
    init_exc_handlers(app)

    return app
