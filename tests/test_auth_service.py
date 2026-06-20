import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock

from app.core.config import settings
from app.services.auth_service import AuthService
from app.core.exceptions import AlreadyExistsError, InvalidCredentialsError, InvalidResetTokenError
from app.dto.input.auth_input import (
    RegisterDTO,
    LoginDTO,
    ForgotPasswordDTO,
    ResetPasswordDTO,
    ChangePasswordDTO,
)


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


# ---- Password reset / change ----


@pytest.mark.asyncio
async def test_forgot_password_sends_email_for_existing_user(mock_session, sample_user):
    service = AuthService(session=mock_session)

    with patch.object(service._user_repo, "get_by_email", return_value=sample_user), \
         patch.object(service._email_service, "send_password_reset", new_callable=AsyncMock) as mock_send:
        await service.request_password_reset(ForgotPasswordDTO(email="test@example.com"))

    mock_send.assert_awaited_once()


@pytest.mark.asyncio
async def test_forgot_password_silent_for_unknown_email(mock_session):
    service = AuthService(session=mock_session)

    with patch.object(service._user_repo, "get_by_email", return_value=None), \
         patch.object(service._email_service, "send_password_reset", new_callable=AsyncMock) as mock_send:
        await service.request_password_reset(ForgotPasswordDTO(email="ghost@example.com"))

    mock_send.assert_not_awaited()


@pytest.mark.asyncio
async def test_reset_password_success(mock_session, sample_user):
    service = AuthService(session=mock_session)
    token = service._generate_reset_token(sample_user)

    with patch.object(service._user_repo, "get_by", return_value=sample_user), \
         patch("app.services.auth_service.pwd_context.hash", return_value="new_hashed_pw"):
        await service.reset_password(ResetPasswordDTO(token=token, new_password="newpassword123"))

    assert sample_user.password_hash == "new_hashed_pw"
    mock_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_reset_password_garbage_token(mock_session):
    service = AuthService(session=mock_session)

    with pytest.raises(InvalidResetTokenError):
        await service.reset_password(ResetPasswordDTO(token="not-a-token", new_password="newpassword123"))


@pytest.mark.asyncio
async def test_reset_password_expired_token(mock_session, sample_user):
    service = AuthService(session=mock_session)
    expired = jwt.encode(
        {
            "sub": str(sample_user.uuid),
            "type": "pwd_reset",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        service._reset_token_key(sample_user),
        algorithm=settings.ALGORITHM,
    )

    with patch.object(service._user_repo, "get_by", return_value=sample_user):
        with pytest.raises(InvalidResetTokenError):
            await service.reset_password(ResetPasswordDTO(token=expired, new_password="newpassword123"))


@pytest.mark.asyncio
async def test_reset_password_invalidated_after_password_change(mock_session, sample_user):
    """Token signed with old hash must fail once the password (hash) changed."""
    service = AuthService(session=mock_session)
    token = service._generate_reset_token(sample_user)
    sample_user.password_hash = "$2b$12$changed_hash"  # simulate a later password change

    with patch.object(service._user_repo, "get_by", return_value=sample_user):
        with pytest.raises(InvalidResetTokenError):
            await service.reset_password(ResetPasswordDTO(token=token, new_password="newpassword123"))


@pytest.mark.asyncio
async def test_change_password_success(mock_session, sample_user):
    service = AuthService(session=mock_session)

    with patch("app.services.auth_service.pwd_context.verify", return_value=True), \
         patch("app.services.auth_service.pwd_context.hash", return_value="new_hashed_pw"):
        await service.change_password(sample_user, ChangePasswordDTO(
            old_password="oldpassword123",
            new_password="newpassword123",
        ))

    assert sample_user.password_hash == "new_hashed_pw"
    mock_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_change_password_wrong_old(mock_session, sample_user):
    service = AuthService(session=mock_session)

    with patch("app.services.auth_service.pwd_context.verify", return_value=False):
        with pytest.raises(InvalidCredentialsError):
            await service.change_password(sample_user, ChangePasswordDTO(
                old_password="wrongpassword",
                new_password="newpassword123",
            ))
