from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsError, AlreadyExistsError
from app.db.models import User, Category, CategoryType
from app.repositories.user_repository import UserRepository
from app.dto.input.auth_input import RegisterDTO, LoginDTO
from app.dto.output.user_output import UserOutputDTO, TokenOutputDTO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

    async def register(self, data: RegisterDTO) -> UserOutputDTO:
        existing = await self._user_repo.get_by_email(data.email)
        if existing:
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
        except Exception:
            await self._session.rollback()
            raise

        return UserOutputDTO.model_validate(user)

    async def login(self, data: LoginDTO) -> TokenOutputDTO:
        user = await self._user_repo.get_by_email(data.email)
        if not user or not pwd_context.verify(data.password, user.password_hash):
            raise InvalidCredentialsError()

        payload = {
            "sub": str(user.uuid),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return TokenOutputDTO(access_token=token)
