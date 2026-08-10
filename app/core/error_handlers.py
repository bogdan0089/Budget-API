from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AlreadyExistsError,
    BudgetExceededError,
    EntityNotFound,
    InsufficientFundsError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    ValidationError,
)

# One place decides the HTTP code for every domain exception, so a router that
# forgets to catch one still answers with the right status instead of a 500.
EXCEPTION_STATUS = {
    EntityNotFound: 404,
    AlreadyExistsError: 409,
    InsufficientFundsError: 422,
    BudgetExceededError: 422,
    InvalidCredentialsError: 401,
    InvalidResetTokenError: 400,
    ValidationError: 400,
}


def register_exception_handlers(app: FastAPI) -> None:
    for exception_type, status_code in EXCEPTION_STATUS.items():
        app.add_exception_handler(exception_type, _make_handler(status_code))


def _make_handler(status_code: int):
    async def handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={"detail": exc.message})

    return handler
