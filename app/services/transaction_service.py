from uuid import UUID
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFound, InsufficientFundsError
from app.db.models import Transaction, TransactionType
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.category_repository import CategoryRepository
from app.dto.input.transaction_input import TransactionCreateDTO
from app.dto.output.transaction_output import TransactionOutputDTO


class TransactionService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repo = TransactionRepository(session=session)
        self._account_repo = AccountRepository(session=session)
        self._category_repo = CategoryRepository(session=session)

    async def create(self, user_id: UUID, data: TransactionCreateDTO) -> TransactionOutputDTO:
        account = await self._account_repo.get(data.account_id)
        if account.user_id != user_id:
            raise EntityNotFound("Account", str(data.account_id))

        if data.category_id:
            category = await self._category_repo.get_by(uuid=data.category_id)
            if not category or category.user_id != user_id:
                raise EntityNotFound("Category", str(data.category_id))

        amount = Decimal(str(data.amount))

        if data.type == TransactionType.EXPENSE:
            if account.balance < amount:
                raise InsufficientFundsError()
            new_balance = account.balance - amount
        else:
            new_balance = account.balance + amount

        for key, value in {"balance": new_balance}.items():
            setattr(account, key, value)

        transaction = Transaction(
            account_id=data.account_id,
            category_id=data.category_id,
            amount=amount,
            type=data.type,
            description=data.description,
            date=data.date or date.today(),
        )
        self._session.add(transaction)

        try:
            await self._session.commit()
            await self._session.refresh(transaction)
        except Exception:
            await self._session.rollback()
            raise

        return TransactionOutputDTO.model_validate(transaction)

    async def list_by_account(self, account_id: UUID, user_id: UUID, limit: int = 50, offset: int = 0) -> list[TransactionOutputDTO]:
        account = await self._account_repo.get(account_id)
        if account.user_id != user_id:
            raise EntityNotFound("Account", str(account_id))
        transactions = await self._repo.list_by_account(account_id, limit, offset)
        return [TransactionOutputDTO.model_validate(t) for t in transactions]
