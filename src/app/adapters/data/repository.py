from app.domain.user import User


class UserRepository:
    def __init__(self) -> None:
        self.users: list[User] = list()

    def get_user(self, id: int) -> User | None:
        result = filter(lambda x: x.id == id, self.users)

        return next(result, None)

    def get_user_by_username(self, username: str) -> User | None:
        result = filter(lambda x: x.username == username, self.users)

        return next(result, None)

    def save_user(self, user: User) -> None:
        self.users.append(user)

    def get_last_inserted_id(self) -> int:
        if not self.users:
            return 1

        return max(map(lambda x: x.id, self.users)) + 1

    def delete_user(self, id: int) -> None:
        user = self.get_user(id)
        self.users.remove(user)
