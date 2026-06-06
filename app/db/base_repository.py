from uuid import UUID
from typing import Any, Generic, Optional, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.base_model import BaseModel
from app.core.exceptions import EntityNotFound, AlreadyExistsError

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]):
        self._session = session
        self._model = model

    async def add(self, obj: T) -> T:
        self._session.add(obj)
        return await self._commit_and_refresh(obj)

    async def stage(self, obj: T) -> T:
        self._session.add(obj)
        await self._session.flush()
        return obj

    async def get(self, uuid: UUID) -> T:
        obj = await self._session.get(self._model, uuid)
        if not obj:
            raise EntityNotFound(entity=self._model.__name__, uuid=str(uuid))
        return obj

    async def get_by(self, **filters) -> Optional[T]:
        stmt = select(self._model).filter_by(**filters)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by(self, **filters) -> list[T]:
        stmt = select(self._model).filter_by(**filters)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, uuid: UUID, data: dict[str, Any]) -> T:
        obj = await self.get(uuid)
        for key, value in data.items():
            setattr(obj, key, value)
        return await self._commit_and_refresh(obj)

    async def delete(self, uuid: UUID) -> None:
        obj = await self.get(uuid)
        await self._session.delete(obj)
        await self._session.commit()

    async def _commit_and_refresh(self, obj: T) -> T:
        try:
            await self._session.commit()
            await self._session.refresh(obj)
            return obj
        except IntegrityError as e:
            await self._session.rollback()
            if "unique" in str(e.orig).lower():
                raise AlreadyExistsError(entity=self._model.__name__)
            raise
        except SQLAlchemyError:
            await self._session.rollback()
            raise
