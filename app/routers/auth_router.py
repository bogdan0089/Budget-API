from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user
from app.db.models import User
from app.dto.input.auth_input import (
    RegisterDTO,
    LoginDTO,
    ForgotPasswordDTO,
    ResetPasswordDTO,
    ChangePasswordDTO,
)
from app.dto.output.user_output import UserOutputDTO, TokenOutputDTO

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(session=session)


@router.post("/register", response_model=UserOutputDTO, status_code=201)
async def register(data: RegisterDTO, service: AuthService = Depends(get_service)):
    return await service.register(data)


@router.post("/login", response_model=TokenOutputDTO)
async def login(data: LoginDTO, service: AuthService = Depends(get_service)):
    return await service.login(data)


@router.post("/forgot-password", status_code=202)
async def forgot_password(data: ForgotPasswordDTO, service: AuthService = Depends(get_service)):
    await service.request_password_reset(data)
    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordDTO, service: AuthService = Depends(get_service)):
    await service.reset_password(data)
    return {"message": "Password updated successfully."}


@router.post("/change-password")
async def change_password(
    data: ChangePasswordDTO,
    user: User = Depends(get_current_user),
    service: AuthService = Depends(get_service),
):
    await service.change_password(user, data)
    return {"message": "Password changed successfully."}
