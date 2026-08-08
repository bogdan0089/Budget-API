import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import date

from app.services.budget_service import BudgetService
from app.core.exceptions import EntityNotFound
from app.dto.input.budget_input import BudgetCreateDTO, BudgetUpdateDTO
from app.db.models import Budget


@pytest.fixture
def sample_budget(sample_user, sample_category):
    budget = MagicMock(spec=Budget)
    budget.uuid = uuid4()
    budget.user_id = sample_user.uuid
    budget.category_id = sample_category.uuid
    budget.month = date(2026, 6, 1)
    budget.limit_amount = Decimal("5000.00")
    budget.category = sample_category
    return budget


@pytest.mark.asyncio
async def test_create_budget(mock_session, sample_user, sample_budget, sample_category):
    service = BudgetService(session=mock_session)

    with patch.object(service._repo, "get_by_user_and_category", return_value=None), \
         patch.object(service._repo, "add", return_value=sample_budget), \
         patch.object(service._repo, "get_with_category", return_value=sample_budget), \
         patch.object(service._transaction_repo, "get_spent_by_category", return_value=Decimal("1000.00")):

        result = await service.create(
            sample_user.uuid,
            BudgetCreateDTO(category_id=sample_category.uuid, month=date(2026, 6, 1), limit_amount=5000.0)
        )

    assert result.limit_amount == Decimal("5000.00")
    assert result.spent_amount == Decimal("1000.00")
    assert result.remaining == Decimal("4000.00")


@pytest.mark.asyncio
async def test_list_budgets(mock_session, sample_user, sample_budget, sample_category):
    service = BudgetService(session=mock_session)

    with patch.object(service._repo, "list_by_user", return_value=[sample_budget]), \
         patch.object(service._transaction_repo, "get_spent_by_category", return_value=Decimal("0.00")):

        result = await service.list_budgets(sample_user.uuid)

    assert len(result) == 1
    assert result[0].category_name == sample_category.name


@pytest.mark.asyncio
async def test_budget_remaining_zero_when_exceeded(mock_session, sample_user, sample_budget, sample_category):
    service = BudgetService(session=mock_session)
    sample_budget.limit_amount = Decimal("1000.00")

    with patch.object(service._repo, "get_by_user_and_category", return_value=None), \
         patch.object(service._repo, "add", return_value=sample_budget), \
         patch.object(service._repo, "get_with_category", return_value=sample_budget), \
         patch.object(service._transaction_repo, "get_spent_by_category", return_value=Decimal("1500.00")):

        result = await service.create(
            sample_user.uuid,
            BudgetCreateDTO(category_id=sample_category.uuid, month=date(2026, 6, 1), limit_amount=1000.0)
        )

    assert result.remaining == Decimal("0")


@pytest.mark.asyncio
async def test_update_budget(mock_session, sample_user, sample_budget, sample_category):
    service = BudgetService(session=mock_session)
    sample_budget.limit_amount = Decimal("8000.00")

    with patch.object(service._repo, "get", return_value=sample_budget), \
         patch.object(service._repo, "update", return_value=sample_budget), \
         patch.object(service._transaction_repo, "get_spent_by_category", return_value=Decimal("0.00")):

        result = await service.update(sample_budget.uuid, sample_user.uuid, BudgetUpdateDTO(limit_amount=8000.0))

    assert result.limit_amount == Decimal("8000.00")


@pytest.mark.asyncio
async def test_update_budget_wrong_user(mock_session, sample_budget):
    service = BudgetService(session=mock_session)
    other_user_id = uuid4()
    sample_budget.user_id = uuid4()

    with patch.object(service._repo, "get", return_value=sample_budget):
        with pytest.raises(EntityNotFound):
            await service.update(sample_budget.uuid, other_user_id, BudgetUpdateDTO(limit_amount=8000.0))


@pytest.mark.asyncio
async def test_delete_budget(mock_session, sample_user, sample_budget):
    service = BudgetService(session=mock_session)

    with patch.object(service._repo, "get", return_value=sample_budget), \
         patch.object(service._repo, "delete", new=AsyncMock()) as mock_delete:

        await service.delete(sample_budget.uuid, sample_user.uuid)

    mock_delete.assert_called_once_with(sample_budget.uuid)


@pytest.mark.asyncio
async def test_spent_is_scoped_to_budget_owner(mock_session, sample_user, sample_budget, sample_category):
    service = BudgetService(session=mock_session)

    with patch.object(service._repo, "list_by_user", return_value=[sample_budget]), \
         patch.object(service._transaction_repo, "get_spent_by_category", return_value=Decimal("0.00")) as mock_spent:

        await service.list_budgets(sample_user.uuid)

    args = mock_spent.call_args.args
    assert args[0] == sample_budget.category_id
    assert args[1] == sample_budget.user_id
