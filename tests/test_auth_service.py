import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from app.services.auth_service import AuthService
from app.core.exceptions import AlreadyExistsError, InvalidCredentialsError
from app.dto.input.auth_input import RegisterDTO, LoginDTO


@pytest.mark.asyncio
async def test_register_success(mock_session, sample_user):
    service = AuthService(session=mock_session)

    with patch.object(service._user_repo, "get_by_email", return_value=None):
        result = await service.register(RegisterDTO(
            email="test@example.com",
            password="password123",
            full_name="Test User"
        ))

    assert result.email == "test@example.com"
    assert result.full_name == "Test User"


@pytest.mark.asyncio
async def test_register_already_exists(mock_session, sample_user):
    service = AuthService(session=mock_session)

    with patch.object(service._user_repo, "get_by_email", return_value=sample_user):
        with pytest.raises(AlreadyExistsError):
            await service.register(RegisterDTO(
                email="test@example.com",
                password="password123",
                full_name="Test User"
            ))


@pytest.mark.asyncio
async def test_login_success(mock_session, sample_user):
    service = AuthService(session=mock_session)

    with patch.object(service._user_repo, "get_by_email", return_value=sample_user), \
         patch("app.services.auth_service.pwd_context.verify", return_value=True):

        result = await service.login(LoginDTO(
            email="test@example.com",
            password="password123"
        ))

    assert result.access_token is not None
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(mock_session, sample_user):
    service = AuthService(session=mock_session)

    with patch.object(service._user_repo, "get_by_email", return_value=sample_user), \
         patch("app.services.auth_service.pwd_context.verify", return_value=False):

        with pytest.raises(InvalidCredentialsError):
            await service.login(LoginDTO(
                email="test@example.com",
                password="wrong_password"
            ))


@pytest.mark.asyncio
async def test_login_user_not_found(mock_session):
    service = AuthService(session=mock_session)

    with patch.object(service._user_repo, "get_by_email", return_value=None):
        with pytest.raises(InvalidCredentialsError):
            await service.login(LoginDTO(
                email="notfound@example.com",
                password="password123"
            ))
