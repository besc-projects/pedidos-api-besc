from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.users.use_cases import (
    AuthenticateUserUseCase,
    RegisterUserUseCase,
)
from app.database import get_db
from app.domain.protocols.user_repository import UserRepositoryProtocol
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository


def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserRepositoryProtocol:
    return SqlAlchemyUserRepository(db)


def get_register_user_use_case(
    repository: UserRepositoryProtocol = Depends(get_user_repository),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(repository)


def get_authenticate_user_use_case(
    repository: UserRepositoryProtocol = Depends(get_user_repository),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(repository)
