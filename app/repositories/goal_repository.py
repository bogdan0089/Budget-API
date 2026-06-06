from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_repository import BaseRepository
from app.db.models import Goal


class GoalRepository(BaseRepository[Goal]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Goal)

    async def list_by_user(self, user_id: UUID) -> list[Goal]:
        return await self.list_by(user_id=user_id)
