import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from decimal import Decimal
from datetime import date

from app.services.transaction_service import TransactionService
from app.core.exceptions import EntityNotFound, InsufficientFundsError
from app.dto.input.transaction_input import TransactionCreateDTO
from app.db.models import TransactionType


@pytest.mark.asyncio
async def test_create_expense_success(mock_session, sample_user, sample_account):
    service = TransactionService(session=mock_session)
    sample_account.balance = Decimal("10000.00")

    with patch.object(service._account_repo, "get", return_value=sample_account):
        result = await service.create(
            sample_user.uuid,
            TransactionCreateDTO(
                account_id=sample_account.uuid,
                amount=500.0,
                type=TransactionType.EXPENSE,
                description="Coffee"
            )
        )

    assert result.amount == Decimal("500.0")
    assert result.type == TransactionType.EXPENSE


@pytest.mark.asyncio
async def test_create_expense_insufficient_funds(mock_session, sample_user, sample_account):
    service = TransactionService(session=mock_session)
    sample_account.balance = Decimal("100.00")

    with patch.object(service._account_repo, "get", return_value=sample_account):
        with pytest.raises(InsufficientFundsError):
            await service.create(
                sample_user.uuid,
                TransactionCreateDTO(
                    account_id=sample_account.uuid,
                    amount=500.0,
                    type=TransactionType.EXPENSE,
                )
            )


@pytest.mark.asyncio
async def test_create_income_increases_balance(mock_session, sample_user, sample_account):
    service = TransactionService(session=mock_session)
    sample_account.balance = Decimal("5000.00")

    with patch.object(service._account_repo, "get", return_value=sample_account):
        await service.create(
            sample_user.uuid,
            TransactionCreateDTO(
                account_id=sample_account.uuid,
                amount=1000.0,
                type=TransactionType.INCOME,
            )
        )

    assert sample_account.balance == Decimal("6000.00")


@pytest.mark.asyncio
async def test_create_transaction_wrong_user(mock_session, sample_account):
    service = TransactionService(session=mock_session)
    other_user_id = uuid4()
    sample_account.user_id = uuid4()

    with patch.object(service._account_repo, "get", return_value=sample_account):
        with pytest.raises(EntityNotFound):
            await service.create(
                other_user_id,
                TransactionCreateDTO(
                    account_id=sample_account.uuid,
                    amount=100.0,
                    type=TransactionType.EXPENSE,
                )
            )
