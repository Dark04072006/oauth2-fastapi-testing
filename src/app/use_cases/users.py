from app.adapters.auth.token import TokenIdProvider
from app.adapters.data.repository import UserRepository
from app.domain.exceptions import UserIsNotAuthenticated
from app.domain.user import User


class RegisterUser:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def execute(self, username: str, password: str) -> User:
        user = User(
            id=self.repository.get_last_inserted_id(),
            username=username,
            password=password,
        )

        self.repository.save_user(user)

        return user


class LoginUser:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def execute(self, username: str, password: str) -> User:
        user = self.repository.get_user_by_username(username)

        if (user is None) or (user.password != password):
            raise UserIsNotAuthenticated("Invalid username or password")

        return user


class GetAuthenticatedUser:
    def __init__(
        self, id_provider: TokenIdProvider, repository: UserRepository
    ) -> None:
        self.id_provider = id_provider
        self.repository = repository

    def execute(self) -> User:
        user_id = self.id_provider.get_current_user_id()

        user = self.repository.get_user(user_id)

        if user is None:
            raise UserIsNotAuthenticated("Invalid token")

        return user


class DeleteAuthenticatedUser:
    def __init__(
        self, id_provider: TokenIdProvider, repository: UserRepository
    ) -> None:
        self.id_provider = id_provider
        self.repository = repository

    def execute(self) -> None:
        user_id = self.id_provider.get_current_user_id()

        user = self.repository.get_user(user_id)

        if user is None:
            raise UserIsNotAuthenticated("Invalid token")

        self.repository.delete_user(user_id)
