from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.api.dependencies.users import (
    get_authenticate_user_use_case,
    get_register_user_use_case,
)
from app.application.use_cases.users.use_cases import (
    AuthenticateUserUseCase,
    RegisterUserUseCase,
)
from app.schemas.users import UserCreate, UserLogin

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/login", summary="Authenticate and get an access token")
async def login_user(
    user_in: UserLogin,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
) -> dict:
    token = await use_case.execute(user_in.username, user_in.password)
    return {"access_token": token, "token_type": "bearer"}


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    user_in: UserCreate,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> JSONResponse:
    user = await use_case.execute(user_in)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "User created successfully.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "company": user.company,
            },
        },
    )


@router.get("/me", summary="Return the authenticated user's data")
async def get_user_data(request: Request) -> dict:
    """Protected endpoint that returns the authenticated user's data."""
    return {"user": request.state.user}
