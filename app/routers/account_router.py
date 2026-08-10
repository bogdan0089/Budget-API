from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.db.models import User
from app.dependencies.auth import get_current_user
from app.services.account_service import AccountService
from app.dto.input.account_input import AccountCreateDTO, AccountUpdateDTO
from app.dto.output.account_output import AccountOutputDTO

router = APIRouter(prefix="/accounts", tags=["accounts"])


async def get_service(session: AsyncSession = Depends(get_db_session)) -> AccountService:
    return AccountService(session=session)


@router.post("", response_model=AccountOutputDTO, status_code=201)
async def create_account(
    data: AccountCreateDTO,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_service),
):
    return await service.create(current_user.uuid, data)


@router.get("", response_model=list[AccountOutputDTO])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_service),
):
    return await service.list_accounts(current_user.uuid)


@router.get("/{account_id}", response_model=AccountOutputDTO)
async def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_service),
):
    return await service.get(account_id, current_user.uuid)


@router.patch("/{account_id}", response_model=AccountOutputDTO)
async def update_account(
    account_id: UUID,
    data: AccountUpdateDTO,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_service),
):
    return await service.update(account_id, current_user.uuid, data)


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_service),
):
    await service.delete(account_id, current_user.uuid)
