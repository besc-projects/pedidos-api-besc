from typing import Optional

import pytest

from app.application.use_cases.users.use_cases import (
    AuthenticateUserUseCase,
    RegisterUserUseCase,
)
from app.core.security import hash_password
from app.domain.entities.user import User
from app.domain.exceptions import ConflictException, UnauthorizedException
from app.schemas.users import UserCreate


class FakeUserRepository:
    def __init__(self) -> None:
        self._items: list[User] = []
        self._next_id = 1

    async def get_by_username(self, username: str) -> Optional[User]:
        return next((u for u in self._items if u.username == username), None)

    async def get_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._items if u.email == email), None)

    async def create(self, user: User) -> User:
        user.id = self._next_id
        self._next_id += 1
        self._items.append(user)
        return user


def _payload(**overrides) -> UserCreate:
    data = {
        "username": "john",
        "email": "john@example.com",
        "password": "secret",
        "company": "acme",
    }
    data.update(overrides)
    return UserCreate.model_validate(data)


async def test_register_user_ok():
    user = await RegisterUserUseCase(FakeUserRepository()).execute(_payload())
    assert user.id == 1
    assert user.hashed_password != "secret"


async def test_register_duplicate_username():
    repository = FakeUserRepository()
    use_case = RegisterUserUseCase(repository)
    await use_case.execute(_payload())
    with pytest.raises(ConflictException):
        await use_case.execute(_payload(email="other@example.com"))


async def test_register_duplicate_email():
    repository = FakeUserRepository()
    use_case = RegisterUserUseCase(repository)
    await use_case.execute(_payload())
    with pytest.raises(ConflictException):
        await use_case.execute(_payload(username="other"))


async def test_authenticate_ok():
    repository = FakeUserRepository()
    repository._items.append(
        User(username="john", email="j@e.com", hashed_password=hash_password("secret"))
    )
    token = await AuthenticateUserUseCase(repository).execute("john", "secret")
    assert isinstance(token, str) and token


async def test_authenticate_invalid_credentials():
    with pytest.raises(UnauthorizedException):
        await AuthenticateUserUseCase(FakeUserRepository()).execute("x", "y")
