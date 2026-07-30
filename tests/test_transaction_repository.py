import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.repositories.transaction_repository import TransactionRepository
from app.db.models import TransactionType


@pytest.mark.asyncio
async def test_list_by_account_type_filter_builds_statement(mock_session):
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = result
    repo = TransactionRepository(session=mock_session)

    transactions = await repo.list_by_account(uuid4(), type=TransactionType.EXPENSE)

    assert transactions == []
    where_clause = str(mock_session.execute.call_args[0][0]).split("WHERE")[1]
    assert "transactions.type = " in where_clause


@pytest.mark.asyncio
async def test_list_by_account_without_type_filter(mock_session):
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = result
    repo = TransactionRepository(session=mock_session)

    await repo.list_by_account(uuid4())

    where_clause = str(mock_session.execute.call_args[0][0]).split("WHERE")[1]
    assert "transactions.type = " not in where_clause
