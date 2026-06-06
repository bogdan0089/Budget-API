from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.db.models import User
from app.dependencies.auth import get_current_user
from app.services.ai_service import AiService
from app.dto.input.ai_input import ChatMessageDTO

router = APIRouter(prefix="/ai", tags=["ai"])


async def get_service(db: AsyncSession = Depends(get_db_session)) -> AiService:
    return AiService(session=db)


@router.get("/analyze", response_model=str)
async def analyze_spending(
    current_user: User = Depends(get_current_user),
    service: AiService = Depends(get_service),
):
    return await service.analyze_spending(current_user.uuid)


@router.post("/chat", response_model=str)
async def chat(
    data: ChatMessageDTO,
    current_user: User = Depends(get_current_user),
    service: AiService = Depends(get_service),
):
    return await service.chat(current_user.uuid, data.message)
