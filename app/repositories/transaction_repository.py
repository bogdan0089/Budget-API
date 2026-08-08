from uuid import UUID
from decimal import Decimal
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base_repository import BaseRepository
from app.db.models import Account, Transaction, TransactionType


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)

    async def list_by_account(
            self,
            account_id: UUID,
            limit: int = 50,
            offset: int = 0,
            type: TransactionType | None = None,
            category_id: UUID | None = None,
            date_from: date | None = None,
            date_to: date | None = None
        ) -> list[Transaction]:
        filters = [Transaction.account_id == account_id]
        if type:
            filters.append(Transaction.type == type)
        if category_id:
            filters.append(Transaction.category_id == category_id)
        if date_from:
            filters.append(Transaction.date >= date_from)
        if date_to:
            filters.append(Transaction.date <= date_to)

        stmt = (
            select(Transaction)
            .where(and_(*filters))
            .options(selectinload(Transaction.category))
            .order_by(Transaction.date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent_by_user(self, user_id: UUID, limit: int = 30) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.uuid)
            .where(Account.user_id == user_id)
            .options(selectinload(Transaction.category))
            .order_by(Transaction.date.desc())
            .limit(limit)
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
