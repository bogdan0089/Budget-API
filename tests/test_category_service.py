import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.repositories.category_repository import CategoryRepository
from app.db.models import Category, CategoryType


@pytest.fixture
def sample_categories(sample_user):
    cat1 = MagicMock(spec=Category)
    cat1.uuid = uuid4()
    cat1.user_id = sample_user.uuid
    cat1.name = "Food"
    cat1.type = CategoryType.EXPENSE
    cat1.icon = "🍕"

    cat2 = MagicMock(spec=Category)
    cat2.uuid = None
    cat2.user_id = None
    cat2.name = "Salary"
    cat2.type = CategoryType.INCOME
    cat2.icon = "💰"

    return [cat1, cat2]


@pytest.mark.asyncio
async def test_list_categories_includes_system(mock_session, sample_user, sample_categories):
    repo = CategoryRepository(session=mock_session)

    with patch.object(repo, "list_for_user", return_value=sample_categories):
        result = await repo.list_for_user(sample_user.uuid)

    assert len(result) == 2
    user_cats = [c for c in result if c.user_id is not None]
    system_cats = [c for c in result if c.user_id is None]
    assert len(user_cats) == 1
    assert len(system_cats) == 1


@pytest.mark.asyncio
async def test_list_categories_empty(mock_session, sample_user):
    repo = CategoryRepository(session=mock_session)

    with patch.object(repo, "list_for_user", return_value=[]):
        result = await repo.list_for_user(sample_user.uuid)

    assert result == []
