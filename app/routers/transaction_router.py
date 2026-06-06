from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.db.models import User
from app.dependencies.auth import get_current_user
from app.services.transaction_service import TransactionService
from app.core.exceptions import EntityNotFound, InsufficientFundsError
from app.dto.input.transaction_input import TransactionCreateDTO
from app.dto.output.transaction_output import TransactionOutputDTO

router = APIRouter(prefix="/transactions", tags=["transactions"])


async def get_service(db: AsyncSession = Depends(get_db_session)) -> TransactionService:
    return TransactionService(session=db)


@router.post("", response_model=TransactionOutputDTO, status_code=201)
async def create_transaction(
    data: TransactionCreateDTO,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_service),
):
    try:
        return await service.create(current_user.uuid, data)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except InsufficientFundsError as e:
        raise HTTPException(status_code=422, detail=e.message)


@router.get("/account/{account_id}", response_model=list[TransactionOutputDTO])
async def list_transactions(
    account_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_service),
):
    try:
        return await service.list_by_account(account_id, current_user.uuid, limit, offset)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
