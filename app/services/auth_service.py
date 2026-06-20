from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsError, AlreadyExistsError, InvalidResetTokenError
from app.db.models import User, Category, CategoryType
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService
from app.dto.input.auth_input import RegisterDTO, LoginDTO, ForgotPasswordDTO, ResetPasswordDTO, ChangePasswordDTO
from app.dto.output.user_output import UserOutputDTO, TokenOutputDTO
from app.utils.logger import get_logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = get_logger(__name__)

DEFAULT_CATEGORIES = [
    {"name": "Їжа", "type": CategoryType.EXPENSE, "icon": "🍕"},
    {"name": "Транспорт", "type": CategoryType.EXPENSE, "icon": "🚗"},
    {"name": "Розваги", "type": CategoryType.EXPENSE, "icon": "🎮"},
    {"name": "Здоров'я", "type": CategoryType.EXPENSE, "icon": "💊"},
    {"name": "Комунальні", "type": CategoryType.EXPENSE, "icon": "🏠"},
    {"name": "Одяг", "type": CategoryType.EXPENSE, "icon": "👕"},
    {"name": "Інші витрати", "type": CategoryType.EXPENSE, "icon": "💸"},
    {"name": "Зарплата", "type": CategoryType.INCOME, "icon": "💰"},
    {"name": "Фріланс", "type": CategoryType.INCOME, "icon": "💻"},
    {"name": "Інші доходи", "type": CategoryType.INCOME, "icon": "📈"},
]


class AuthService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._user_repo = UserRepository(session=session)
        self._email_service = EmailService()

    async def register(self, data: RegisterDTO) -> UserOutputDTO:
        existing = await self._user_repo.get_by_email(data.email)
        if existing:
            logger.warning(f"Registration attempt with existing email: {data.email}")
            raise AlreadyExistsError("User")

        user = User(
            email=data.email,
            password_hash=pwd_context.hash(data.password),
            full_name=data.full_name,
            is_active=True,
        )
        self._session.add(user)
        await self._session.flush()

        for cat in DEFAULT_CATEGORIES:
            self._session.add(Category(
                user_id=user.uuid,
                name=cat["name"],
                type=cat["type"],
                icon=cat["icon"],
            ))

        try:
            await self._session.commit()
            await self._session.refresh(user)
        except Exception as e:
            await self._session.rollback()
            logger.error(f"Registration failed for {data.email}: {e}", exc_info=True)
            raise

        logger.info(f"User registered: {user.uuid}, email={data.email}")
        return UserOutputDTO.model_validate(user)

    async def login(self, data: LoginDTO) -> TokenOutputDTO:
        user = await self._user_repo.get_by_email(data.email)
        if not user or not pwd_context.verify(data.password, user.password_hash):
            logger.warning(f"Failed login attempt: {data.email}")
            raise InvalidCredentialsError()

        payload = {
            "sub": str(user.uuid),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.info(f"User logged in: {user.uuid}")
        return TokenOutputDTO(access_token=token)

    def _reset_token_key(self, user: User) -> str:
        return f"{settings.SECRET_KEY}{user.password_hash}"

    def _generate_reset_token(self, user: User) -> str:
        payload = {
            "sub": str(user.uuid),
            "type": "pwd_reset",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, self._reset_token_key(user), algorithm=settings.ALGORITHM)

    async def request_password_reset(self, data: ForgotPasswordDTO) -> None:
        user = await self._user_repo.get_by_email(data.email)
        if not user or not user.is_active:
            # Never reveal whether the email exists.
            logger.info(f"Password reset requested for unknown email: {data.email}")
            return

        token = self._generate_reset_token(user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        await self._email_service.send_password_reset(user.email, user.full_name, reset_link)
        logger.info(f"Password reset link issued: {user.uuid}")

    async def reset_password(self, data: ResetPasswordDTO) -> None:
        try:
            unverified = jwt.decode(data.token, options={"verify_signature": False})
            user_id = UUID(unverified["sub"])
        except Exception:
            raise InvalidResetTokenError()

        user = await self._user_repo.get_by(uuid=user_id)
        if not user:
            raise InvalidResetTokenError()

        try:
            payload = jwt.decode(data.token, self._reset_token_key(user), algorithms=[settings.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise InvalidResetTokenError("Reset link has expired")
        except jwt.PyJWTError:
            raise InvalidResetTokenError()

        if payload.get("type") != "pwd_reset":
            raise InvalidResetTokenError()

        user.password_hash = pwd_context.hash(data.new_password)
        await self._session.commit()
        logger.info(f"Password reset completed: {user.uuid}")

    async def change_password(self, user: User, data: ChangePasswordDTO) -> None:
        if not pwd_context.verify(data.old_password, user.password_hash):
            logger.warning(f"Wrong current password on change: {user.uuid}")
            raise InvalidCredentialsError()

        user.password_hash = pwd_context.hash(data.new_password)
        await self._session.commit()
        logger.info(f"Password changed: {user.uuid}")
