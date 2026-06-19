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


@pytest.mark.asyncio
async def test_list_by_account_no_filters(mock_session, sample_user, sample_account, sample_transaction):
    service = TransactionService(session=mock_session)

    with patch.object(service._account_repo, "get", return_value=sample_account), \
         patch.object(service._repo, "list_by_account", return_value=[sample_transaction]) as mock_list:

        result = await service.list_by_account(sample_account.uuid, sample_user.uuid)

    mock_list.assert_called_once_with(sample_account.uuid, 50, 0, None, None, None, None)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_list_by_account_with_type_filter(mock_session, sample_user, sample_account, sample_transaction):
    service = TransactionService(session=mock_session)

    with patch.object(service._account_repo, "get", return_value=sample_account), \
         patch.object(service._repo, "list_by_account", return_value=[sample_transaction]) as mock_list:

        await service.list_by_account(sample_account.uuid, sample_user.uuid, type="expense")

    mock_list.assert_called_once_with(sample_account.uuid, 50, 0, "expense", None, None, None)


@pytest.mark.asyncio
async def test_list_by_account_with_date_filter(mock_session, sample_user, sample_account, sample_transaction):
    service = TransactionService(session=mock_session)
    date_from = date(2026, 1, 1)
    date_to = date(2026, 6, 30)

    with patch.object(service._account_repo, "get", return_value=sample_account), \
         patch.object(service._repo, "list_by_account", return_value=[sample_transaction]) as mock_list:

        await service.list_by_account(
            sample_account.uuid, sample_user.uuid, date_from=date_from, date_to=date_to
        )

    mock_list.assert_called_once_with(sample_account.uuid, 50, 0, None, None, date_from, date_to)


@pytest.mark.asyncio
async def test_list_by_account_wrong_user(mock_session, sample_account):
    service = TransactionService(session=mock_session)
    other_user_id = uuid4()
    sample_account.user_id = uuid4()

    with patch.object(service._account_repo, "get", return_value=sample_account):
        with pytest.raises(EntityNotFound):
            await service.list_by_account(sample_account.uuid, other_user_id)
