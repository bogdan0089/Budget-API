from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFound, ValidationError
from app.db.models import Goal
from app.repositories.goal_repository import GoalRepository
from app.dto.input.goal_input import GoalCreateDTO, GoalDepositDTO
from app.dto.output.goal_output import GoalOutputDTO
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GoalService:
    def __init__(self, session: AsyncSession):
        self._repo = GoalRepository(session=session)

    async def create(self, user_id: UUID, data: GoalCreateDTO) -> GoalOutputDTO:
        goal = Goal(
            user_id=user_id,
            name=data.name,
            target_amount=data.target_amount,
            deadline=data.deadline,
        )
        goal = await self._repo.add(goal)
        logger.info(f"Goal created: goal={goal.uuid}, user={user_id}, target={data.target_amount}")
        return self._to_dto(goal)

    async def list_goals(self, user_id: UUID) -> list[GoalOutputDTO]:
        goals = await self._repo.list_by_user(user_id)
        return [self._to_dto(g) for g in goals]

    async def deposit(self, uuid: UUID, user_id: UUID, data: GoalDepositDTO) -> GoalOutputDTO:
        goal = await self._repo.get(uuid)
        if goal.user_id != user_id:
            logger.warning(f"Unauthorized goal access: user={user_id}, goal={uuid}")
            raise EntityNotFound("Goal", str(uuid))
        if goal.is_completed:
            logger.warning(f"Deposit to completed goal: goal={uuid}, user={user_id}")
            raise ValidationError("Goal is already completed")

        new_amount = Decimal(str(goal.current_amount)) + Decimal(str(data.amount))
        is_completed = new_amount >= Decimal(str(goal.target_amount))
        goal = await self._repo.update(uuid, {"current_amount": new_amount, "is_completed": is_completed})
        if is_completed:
            logger.info(f"Goal completed: goal={uuid}, user={user_id}")
        else:
            logger.info(f"Goal deposit: goal={uuid}, user={user_id}, amount={data.amount}, total={new_amount}")
        return self._to_dto(goal)

    async def delete(self, uuid: UUID, user_id: UUID) -> None:
        goal = await self._repo.get(uuid)
        if goal.user_id != user_id:
            logger.warning(f"Unauthorized goal delete: user={user_id}, goal={uuid}")
            raise EntityNotFound("Goal", str(uuid))
        await self._repo.delete(uuid)
        logger.info(f"Goal deleted: goal={uuid}, user={user_id}")

    def _to_dto(self, goal: Goal) -> GoalOutputDTO:
        target = Decimal(str(goal.target_amount))
        current = Decimal(str(goal.current_amount))
        progress = float(current / target * 100) if target > 0 else 0.0
        return GoalOutputDTO(
            uuid=goal.uuid,
            name=goal.name,
            target_amount=target,
            current_amount=current,
            progress_percent=round(progress, 1),
            deadline=goal.deadline,
            is_completed=goal.is_completed,
            created_at=goal.created_at,
        )
