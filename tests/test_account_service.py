import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from decimal import Decimal

from app.services.account_service import AccountService
from app.core.exceptions import EntityNotFound
from app.dto.input.account_input import AccountCreateDTO, AccountUpdateDTO
from app.db.models import AccountType


@pytest.mark.asyncio
async def test_create_account(mock_session, sample_user, sample_account):
    service = AccountService(session=mock_session)

    with patch.object(service._repo, "add", return_value=sample_account):
        result = await service.create(
            sample_user.uuid,
            AccountCreateDTO(name="My Card", type=AccountType.CARD, currency="UAH")
        )

    assert result.name == sample_account.name
    assert result.balance == sample_account.balance


@pytest.mark.asyncio
async def test_list_accounts(mock_session, sample_user, sample_account):
    service = AccountService(session=mock_session)

    with patch.object(service._repo, "list_by_user", return_value=[sample_account]):
        result = await service.list_accounts(sample_user.uuid)

    assert len(result) == 1
    assert result[0].name == sample_account.name


@pytest.mark.asyncio
async def test_get_account_success(mock_session, sample_user, sample_account):
    service = AccountService(session=mock_session)

    with patch.object(service._repo, "get", return_value=sample_account):
        result = await service.get(sample_account.uuid, sample_user.uuid)

    assert result.uuid == sample_account.uuid


@pytest.mark.asyncio
async def test_get_account_wrong_user(mock_session, sample_account):
    service = AccountService(session=mock_session)
    other_user_id = uuid4()
    sample_account.user_id = uuid4()

    with patch.object(service._repo, "get", return_value=sample_account):
        with pytest.raises(EntityNotFound):
            await service.get(sample_account.uuid, other_user_id)


@pytest.mark.asyncio
async def test_delete_account(mock_session, sample_user, sample_account):
    service = AccountService(session=mock_session)

    with patch.object(service._repo, "get", return_value=sample_account), \
         patch.object(service._repo, "delete", new=AsyncMock()) as mock_delete:
        await service.delete(sample_account.uuid, sample_user.uuid)

    mock_delete.assert_called_once_with(sample_account.uuid)
