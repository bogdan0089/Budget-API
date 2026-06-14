from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.db.models import User
from app.dependencies.auth import get_current_user
from app.services.goal_service import GoalService
from app.core.exceptions import EntityNotFound, ValidationError
from app.dto.input.goal_input import GoalCreateDTO, GoalDepositDTO
from app.dto.output.goal_output import GoalOutputDTO

router = APIRouter(prefix="/goals", tags=["goals"])


async def get_service(session: AsyncSession = Depends(get_db_session)) -> GoalService:
    return GoalService(session=session)


@router.post("", response_model=GoalOutputDTO, status_code=201)
async def create_goal(
    data: GoalCreateDTO,
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_service),
):
    return await service.create(current_user.uuid, data)


@router.get("", response_model=list[GoalOutputDTO])
async def list_goals(
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_service),
):
    return await service.list_goals(current_user.uuid)


@router.post("/{goal_id}/deposit", response_model=GoalOutputDTO)
async def deposit_to_goal(
    goal_id: UUID,
    data: GoalDepositDTO,
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_service),
):
    try:
        return await service.deposit(goal_id, current_user.uuid, data)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_service),
):
    try:
        await service.delete(goal_id, current_user.uuid)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
