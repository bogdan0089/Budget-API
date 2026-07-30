import pytest
from unittest.mock import patch
from uuid import uuid4

from app.services import ai_service
from app.services.ai_service import AiService, AI_DISABLED_MESSAGE


@pytest.mark.asyncio
async def test_analyze_spending_without_api_key(mock_session):
    with patch.object(ai_service.settings, "GROQ_API_KEY", ""):
        service = AiService(session=mock_session)
        result = await service.analyze_spending(uuid4())

    assert result == AI_DISABLED_MESSAGE


@pytest.mark.asyncio
async def test_chat_without_api_key(mock_session):
    with patch.object(ai_service.settings, "GROQ_API_KEY", ""):
        service = AiService(session=mock_session)
        result = await service.chat(uuid4(), "How much did I spend?")

    assert result == AI_DISABLED_MESSAGE


@pytest.mark.asyncio
async def test_analyze_spending_without_accounts(mock_session):
    with patch.object(ai_service.settings, "GROQ_API_KEY", "test-key"):
        service = AiService(session=mock_session)
        with patch.object(service._account_repo, "list_by_user", return_value=[]):
            result = await service.analyze_spending(uuid4())

    assert "No accounts found" in result
