import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

from app.db.models import User, Account, AccountType, Transaction, TransactionType, Goal, Budget, Category


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()

    async def auto_refresh(obj, *args):
        if hasattr(obj, "uuid") and getattr(obj, "uuid", None) is None:
            obj.uuid = uuid4()
        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = datetime.now()

    session.refresh.side_effect = auto_refresh
    return session


@pytest.fixture
def sample_user():
    user = MagicMock(spec=User)
    user.uuid = uuid4()
    user.email = "test@example.com"
    user.password_hash = "$2b$12$test_hash"
    user.full_name = "Test User"
    user.is_active = True
    user.created_at = datetime.now()
    return user


@pytest.fixture
def sample_account(sample_user):
    account = MagicMock(spec=Account)
    account.uuid = uuid4()
    account.user_id = sample_user.uuid
    account.name = "My Card"
    account.type = AccountType.CARD
    account.balance = Decimal("10000.00")
    account.currency = "UAH"
    account.is_active = True
    account.created_at = datetime.now()
    return account


@pytest.fixture
def sample_transaction(sample_account):
    transaction = MagicMock(spec=Transaction)
    transaction.uuid = uuid4()
    transaction.account_id = sample_account.uuid
    transaction.category_id = None
    transaction.amount = Decimal("500.00")
    transaction.type = TransactionType.EXPENSE
    transaction.description = "Coffee"
    transaction.date = date.today()
    transaction.category = None
    transaction.created_at = datetime.now()
    return transaction


@pytest.fixture
def sample_goal(sample_user):
    goal = MagicMock(spec=Goal)
    goal.uuid = uuid4()
    goal.user_id = sample_user.uuid
    goal.name = "MacBook"
    goal.target_amount = Decimal("50000.00")
    goal.current_amount = Decimal("10000.00")
    goal.deadline = date(2026, 12, 31)
    goal.is_completed = False
    goal.created_at = datetime.now()
    return goal


@pytest.fixture
def sample_category(sample_user):
    category = MagicMock(spec=Category)
    category.uuid = uuid4()
    category.user_id = sample_user.uuid
    category.name = "Food"
    category.type = "expense"
    category.icon = "🍕"
    return category
