from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_repository import BaseRepository
from app.db.models import Account


class AccountRepository(BaseRepository[Account]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Account)

    async def list_by_user(self, user_id: UUID) -> list[Account]:
        return await self.list_by(user_id=user_id, is_active=True)
