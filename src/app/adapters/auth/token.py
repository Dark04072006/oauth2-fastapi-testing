import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

from jose import JWTError
from jose.jwt import decode, encode

from app.domain.exceptions import UserIsNotAuthenticated

Algorithm = Literal[
    "HS256",
    "HS384",
    "HS512",
    "RS256",
    "RS384",
    "RS512",
]


@dataclass(frozen=True)
class JwtTokenOptions:
    secret: str
    expires: timedelta
    algorithm: Algorithm

    @staticmethod
    def from_env() -> "JwtTokenOptions":
        return JwtTokenOptions(
            secret=os.getenv("JWT_SECRET", "SECRET"),
            expires=timedelta(minutes=int(os.getenv("JWT_EXPIRES_IN_MINUTES", "60"))),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        )


class JwtTokenProcessor:
    def __init__(self, jwt_options: JwtTokenOptions) -> None:
        self.jwt_options = jwt_options

    def generate_token(self, user_id: int) -> str:
        issued_at = datetime.now(UTC)
        expiration_time = issued_at + self.jwt_options.expires

        claims = {
            "iat": issued_at,
            "exp": expiration_time,
            "sub": str(user_id),
        }

        return encode(claims, self.jwt_options.secret, self.jwt_options.algorithm)

    def validate_token(self, token: str) -> int:
        try:
            payload = decode(
                token, self.jwt_options.secret, [self.jwt_options.algorithm]
            )

            return int(payload["sub"])

        except (JWTError, ValueError, KeyError):
            raise UserIsNotAuthenticated("Invalid credentials")


class TokenIdProvider:
    def __init__(self, token_processor: JwtTokenProcessor, token: str) -> None:
        self.token_processor = token_processor
        self.token = token

    def get_current_user_id(self) -> int:
        return self.token_processor.validate_token(self.token)
