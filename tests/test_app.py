import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.error_handlers import EXCEPTION_STATUS, register_exception_handlers
from main import app


def test_health_returns_ok():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("exception_type,status_code", list(EXCEPTION_STATUS.items()))
def test_domain_exception_maps_to_status_code(exception_type, status_code):
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/boom")
    async def boom():
        raise exception_type()

    with TestClient(test_app) as client:
        response = client.get("/boom")

    assert response.status_code == status_code
    assert response.json()["detail"]


def test_cors_origin_list_splits_and_trims():
    settings = Settings(CORS_ORIGINS="http://a.test, http://b.test ,")

    assert settings.CORS_ORIGIN_LIST == ["http://a.test", "http://b.test"]
