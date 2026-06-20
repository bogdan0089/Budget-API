from uuid import UUID
from decimal import Decimal
from calendar import monthrange
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFound, AlreadyExistsError
from app.db.models import Budget
from app.repositories.budget_repository import BudgetRepository
from app.repositories.transaction_repository import TransactionRepository
from app.dto.input.budget_input import BudgetCreateDTO, BudgetUpdateDTO
from app.dto.output.budget_output import BudgetOutputDTO
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BudgetService:
    def __init__(self, session: AsyncSession):
        self._repo = BudgetRepository(session=session)
        self._transaction_repo = TransactionRepository(session=session)

    async def create(self, user_id: UUID, data: BudgetCreateDTO) -> BudgetOutputDTO:
        month_start = data.month.replace(day=1)

        existing = await self._repo.get_by_user_and_category(user_id, data.category_id, month_start)
        if existing:
            logger.warning(f"Duplicate budget: user={user_id}, category={data.category_id}, month={month_start}")
            raise AlreadyExistsError("Budget for this category and month")

        budget = Budget(
            user_id=user_id,
            category_id=data.category_id,
            month=month_start,
            limit_amount=data.limit_amount,
        )
        budget = await self._repo.add(budget)
        budget = await self._repo.get_with_category(budget.uuid)
        logger.info(f"Budget created: budget={budget.uuid}, user={user_id}, limit={data.limit_amount}, month={month_start}")
        return await self._to_dto(budget)

    async def list_budgets(self, user_id: UUID) -> list[BudgetOutputDTO]:
        budgets = await self._repo.list_by_user(user_id)
        return [await self._to_dto(b) for b in budgets]

    async def update(self, uuid: UUID, user_id: UUID, data: BudgetUpdateDTO) -> BudgetOutputDTO:
        budget = await self._repo.get(uuid)
        if budget.user_id != user_id:
            logger.warning(f"Unauthorized budget update: user={user_id}, budget={uuid}")
            raise EntityNotFound("Budget", str(uuid))
        budget = await self._repo.update(uuid, {"limit_amount": data.limit_amount})
        logger.info(f"Budget updated: budget={uuid}, user={user_id}, new_limit={data.limit_amount}")
        return await self._to_dto(budget)

    async def delete(self, uuid: UUID, user_id: UUID) -> None:
        budget = await self._repo.get(uuid)
        if budget.user_id != user_id:
            logger.warning(f"Unauthorized budget delete: user={user_id}, budget={uuid}")
            raise EntityNotFound("Budget", str(uuid))
        await self._repo.delete(uuid)
        logger.info(f"Budget deleted: budget={uuid}, user={user_id}")

    async def _to_dto(self, budget: Budget) -> BudgetOutputDTO:
        month_start = budget.month.replace(day=1)
        days_in_month = monthrange(month_start.year, month_start.month)[1]
        month_end = month_start.replace(day=days_in_month)

        spent = await self._transaction_repo.get_spent_by_category(
            budget.category_id, month_start, month_end
        )
        spent = Decimal(str(spent))
        limit = Decimal(str(budget.limit_amount))

        category_name = budget.category.name if budget.category else ""

        return BudgetOutputDTO(
            uuid=budget.uuid,
            category_id=budget.category_id,
            category_name=category_name,
            month=budget.month,
            limit_amount=limit,
            spent_amount=spent,
            remaining=max(limit - spent, Decimal("0")),
        )
