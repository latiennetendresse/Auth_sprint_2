import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from core.logging import LoggingRoute
from schemas.base import HTTPExceptionResponse
from schemas.users import UserCreate, UserResponse
from services.user import UserService, get_user_service

logger = logging.getLogger(__name__)

get_access_token = HTTPBearer()

router = APIRouter(route_class=LoggingRoute)


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Регистрация",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": HTTPExceptionResponse},
    },
)
async def register(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await user_service.get_user_by_email(user_create.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    return await user_service.create_user(user_create)
