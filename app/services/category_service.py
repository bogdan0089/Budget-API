from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repository import CategoryRepository
from app.dto.output.transaction_output import CategoryShortDTO


class CategoryService:
    def __init__(self, session: AsyncSession):
        self._repo = CategoryRepository(session=session)

    async def list_categories(self, user_id: UUID) -> list[CategoryShortDTO]:
        categories = await self._repo.list_for_user(user_id)
        return [CategoryShortDTO.model_validate(c) for c in categories]
