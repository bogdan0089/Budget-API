import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from decimal import Decimal

from app.services.goal_service import GoalService
from app.core.exceptions import EntityNotFound, ValidationError
from app.dto.input.goal_input import GoalCreateDTO, GoalDepositDTO
from app.db.models import Goal


@pytest.mark.asyncio
async def test_create_goal(mock_session, sample_user, sample_goal):
    service = GoalService(session=mock_session)

    with patch.object(service._repo, "add", return_value=sample_goal):
        result = await service.create(
            sample_user.uuid,
            GoalCreateDTO(name="MacBook", target_amount=50000.0)
        )

    assert result.name == sample_goal.name
    assert result.target_amount == sample_goal.target_amount


@pytest.mark.asyncio
async def test_deposit_increases_amount(mock_session, sample_user, sample_goal):
    service = GoalService(session=mock_session)
    sample_goal.current_amount = Decimal("10000.00")
    sample_goal.target_amount = Decimal("50000.00")
    sample_goal.is_completed = False

    updated_goal = MagicMock(spec=Goal)
    updated_goal.uuid = sample_goal.uuid
    updated_goal.user_id = sample_goal.user_id
    updated_goal.name = sample_goal.name
    updated_goal.target_amount = sample_goal.target_amount
    updated_goal.current_amount = Decimal("15000.00")
    updated_goal.is_completed = False
    updated_goal.deadline = sample_goal.deadline
    updated_goal.created_at = sample_goal.created_at

    with patch.object(service._repo, "get", return_value=sample_goal), \
         patch.object(service._repo, "update", return_value=updated_goal):

        result = await service.deposit(
            sample_goal.uuid,
            sample_user.uuid,
            GoalDepositDTO(amount=5000.0)
        )

    assert result.current_amount == Decimal("15000.00")


@pytest.mark.asyncio
async def test_deposit_completes_goal(mock_session, sample_user, sample_goal):
    service = GoalService(session=mock_session)
    sample_goal.current_amount = Decimal("48000.00")
    sample_goal.target_amount = Decimal("50000.00")
    sample_goal.is_completed = False

    completed_goal = MagicMock(spec=Goal)
    completed_goal.uuid = sample_goal.uuid
    completed_goal.user_id = sample_goal.user_id
    completed_goal.name = sample_goal.name
    completed_goal.target_amount = sample_goal.target_amount
    completed_goal.current_amount = Decimal("50000.00")
    completed_goal.is_completed = True
    completed_goal.deadline = sample_goal.deadline
    completed_goal.created_at = sample_goal.created_at

    with patch.object(service._repo, "get", return_value=sample_goal), \
         patch.object(service._repo, "update", return_value=completed_goal):

        result = await service.deposit(
            sample_goal.uuid,
            sample_user.uuid,
            GoalDepositDTO(amount=2000.0)
        )

    assert result.is_completed is True


@pytest.mark.asyncio
async def test_deposit_to_completed_goal_raises(mock_session, sample_user, sample_goal):
    service = GoalService(session=mock_session)
    sample_goal.is_completed = True

    with patch.object(service._repo, "get", return_value=sample_goal):
        with pytest.raises(ValidationError):
            await service.deposit(
                sample_goal.uuid,
                sample_user.uuid,
                GoalDepositDTO(amount=1000.0)
            )


@pytest.mark.asyncio
async def test_deposit_wrong_user(mock_session, sample_goal):
    service = GoalService(session=mock_session)
    other_user_id = uuid4()
    sample_goal.user_id = uuid4()
    sample_goal.is_completed = False

    with patch.object(service._repo, "get", return_value=sample_goal):
        with pytest.raises(EntityNotFound):
            await service.deposit(
                sample_goal.uuid,
                other_user_id,
                GoalDepositDTO(amount=1000.0)
            )


@pytest.mark.asyncio
async def test_progress_percent(mock_session, sample_user, sample_goal):
    service = GoalService(session=mock_session)
    sample_goal.current_amount = Decimal("25000.00")
    sample_goal.target_amount = Decimal("50000.00")

    with patch.object(service._repo, "list_by_user", return_value=[sample_goal]):
        result = await service.list_goals(sample_user.uuid)

    assert result[0].progress_percent == 50.0
