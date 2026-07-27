from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.domain.entities.user import User
from app.domain.exceptions import ConflictException, UnauthorizedException
from app.domain.protocols.user_repository import UserRepositoryProtocol
from app.schemas.users import UserCreate


class RegisterUserUseCase:
    """Register a new user, enforcing unique username and email."""

    def __init__(self, repository: UserRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: UserCreate) -> User:
        if await self._repository.get_by_username(data.username) is not None:
            raise ConflictException("Username already exists.")
        if await self._repository.get_by_email(data.email) is not None:
            raise ConflictException("Email already registered.")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            company=data.company,
        )
        return await self._repository.create(user)


class AuthenticateUserUseCase:
    """Authenticate a user and issue an access token."""

    def __init__(self, repository: UserRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, username: str, password: str) -> str:
        user = await self._repository.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid credentials.")
        return create_access_token(user.username)
