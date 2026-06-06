from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.db.models import User
from app.dependencies.auth import get_current_user
from app.services.budget_service import BudgetService
from app.core.exceptions import EntityNotFound, AlreadyExistsError
from app.dto.input.budget_input import BudgetCreateDTO, BudgetUpdateDTO
from app.dto.output.budget_output import BudgetOutputDTO

router = APIRouter(prefix="/budgets", tags=["budgets"])


async def get_service(db: AsyncSession = Depends(get_db_session)) -> BudgetService:
    return BudgetService(session=db)


@router.post("", response_model=BudgetOutputDTO, status_code=201)
async def create_budget(
    data: BudgetCreateDTO,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_service),
):
    try:
        return await service.create(current_user.uuid, data)
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)


@router.get("", response_model=list[BudgetOutputDTO])
async def list_budgets(
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_service),
):
    return await service.list_budgets(current_user.uuid)


@router.patch("/{budget_id}", response_model=BudgetOutputDTO)
async def update_budget(
    budget_id: UUID,
    data: BudgetUpdateDTO,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_service),
):
    try:
        return await service.update(budget_id, current_user.uuid, data)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.delete("/{budget_id}", status_code=204)
async def delete_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_service),
):
    try:
        await service.delete(budget_id, current_user.uuid)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
