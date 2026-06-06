from uuid import UUID
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_repository import BaseRepository
from app.db.models import Category


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Category)

    async def list_for_user(self, user_id: UUID) -> list[Category]:
        stmt = select(Category).where(
            or_(Category.user_id == user_id, Category.user_id.is_(None))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
