from uuid import UUID
from decimal import Decimal
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base_repository import BaseRepository
from app.db.models import Transaction, TransactionType


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)

    async def list_by_account(self, account_id: UUID, limit: int = 50, offset: int = 0) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .options(selectinload(Transaction.category))
            .order_by(Transaction.date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_spent_by_category(self, category_id: UUID, month_start: date, month_end: date) -> Decimal:
        stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            and_(
                Transaction.category_id == category_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= month_start,
                Transaction.date <= month_end,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar()
