from uuid import UUID
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base_repository import BaseRepository
from app.db.models import Budget


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Budget)

    async def list_by_user(self, user_id: UUID) -> list[Budget]:
        stmt = (
            select(Budget)
            .where(Budget.user_id == user_id)
            .options(selectinload(Budget.category))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_category(self, uuid: UUID) -> Budget | None:
        stmt = (
            select(Budget)
            .where(Budget.uuid == uuid)
            .options(selectinload(Budget.category))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_category(self, user_id: UUID, category_id: UUID, month: date) -> Budget | None:
        stmt = select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.month == month,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
