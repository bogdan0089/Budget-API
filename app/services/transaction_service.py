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

from app.utils.logger import get_logger


logger = get_logger(__name__)


class TransactionService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repo = TransactionRepository(session=session)
        self._account_repo = AccountRepository(session=session)
        self._category_repo = CategoryRepository(session=session)

    async def create(self, user_id: UUID, data: TransactionCreateDTO) -> TransactionOutputDTO:
        account = await self._account_repo.get(data.account_id)
        if account.user_id != user_id:
            logger.warning(f"Unauthorized account access: user={user_id}, account={data.account_id}")
            raise EntityNotFound("Account", str(data.account_id))

        if data.category_id:
            category = await self._category_repo.get_by(uuid=data.category_id)
            if not category or category.user_id != user_id:
                raise EntityNotFound("Category", str(data.category_id))

        amount = Decimal(str(data.amount))

        if data.type == TransactionType.EXPENSE:
            if account.balance < amount:
                logger.warning(f"Insufficient funds: user={user_id}, account={data.account_id}, amount={amount}")
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
        except Exception as e:
            await self._session.rollback()
            logger.error(f"Transaction commit failed: user={user_id}, error={e}", exc_info=True)
            raise

        logger.info(f"Transaction created: tx={transaction.uuid}, user={user_id}, amount={amount}, type={data.type}")
        return TransactionOutputDTO.model_validate(transaction)

    async def list_by_account(
        self,
        account_id: UUID,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        type: TransactionType | None = None,
        category_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[TransactionOutputDTO]:
        account = await self._account_repo.get(account_id)
        if account.user_id != user_id:
            logger.warning(f"Unauthorized account access: user={user_id}, account={account_id}")
            raise EntityNotFound("Account", str(account_id))
        transactions = await self._repo.list_by_account(account_id, limit, offset, type, category_id, date_from, date_to)
        return [TransactionOutputDTO.model_validate(t) for t in transactions]
