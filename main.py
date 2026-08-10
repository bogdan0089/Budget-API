from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth_router import router as auth_router
from app.routers.account_router import router as account_router
from app.routers.transaction_router import router as transaction_router
from app.routers.budget_router import router as budget_router
from app.routers.goal_router import router as goal_router
from app.routers.ai_router import router as ai_router
from app.routers.category_router import router as category_router

from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


app = FastAPI(title="Smart Budget API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGIN_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(budget_router)
app.include_router(goal_router)
app.include_router(ai_router)
app.include_router(category_router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
