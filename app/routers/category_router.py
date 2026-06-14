from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.db.models import User
from app.dependencies.auth import get_current_user
from app.services.category_service import CategoryService
from app.dto.output.transaction_output import CategoryShortDTO

router = APIRouter(prefix="/categories", tags=["categories"])


async def get_service(session: AsyncSession = Depends(get_db_session)) -> CategoryService:
    return CategoryService(session=session)


@router.get("", response_model=list[CategoryShortDTO])
async def list_categories(
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_service),
):
    return await service.list_categories(current_user.uuid)
