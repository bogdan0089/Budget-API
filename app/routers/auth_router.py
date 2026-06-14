from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.auth_service import AuthService
from app.core.exceptions import AlreadyExistsError, InvalidCredentialsError
from app.dto.input.auth_input import RegisterDTO, LoginDTO
from app.dto.output.user_output import UserOutputDTO, TokenOutputDTO

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(session=session)


@router.post("/register", response_model=UserOutputDTO, status_code=201)
async def register(data: RegisterDTO, service: AuthService = Depends(get_service)):
    try:
        return await service.register(data)
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)


@router.post("/login", response_model=TokenOutputDTO)
async def login(data: LoginDTO, service: AuthService = Depends(get_service)):
    try:
        return await service.login(data)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=e.message)
