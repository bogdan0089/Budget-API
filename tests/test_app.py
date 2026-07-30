from fastapi.testclient import TestClient

from app.core.config import Settings
from main import app


def test_health_returns_ok():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_origin_list_splits_and_trims():
    settings = Settings(CORS_ORIGINS="http://a.test, http://b.test ,")

    assert settings.CORS_ORIGIN_LIST == ["http://a.test", "http://b.test"]
