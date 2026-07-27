from typing import Optional, Protocol

from app.domain.entities.user import User


class UserRepositoryProtocol(Protocol):
    """Persistence contract for users."""

    async def get_by_username(self, username: str) -> Optional[User]:
        ...

    async def get_by_email(self, email: str) -> Optional[User]:
        ...

    async def create(self, user: User) -> User:
        ...
