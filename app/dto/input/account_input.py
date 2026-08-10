from pydantic import BaseModel, Field
from app.db.models import AccountType

# Mirrors the column lengths in app/db/models.py — longer values would only
# fail at the database level with a 500.
NAME_MAX = 100
CURRENCY_MAX = 10


class AccountCreateDTO(BaseModel):
    name: str = Field(min_length=1, max_length=NAME_MAX)
    type: AccountType
    currency: str = Field(default="UAH", min_length=1, max_length=CURRENCY_MAX)


class AccountUpdateDTO(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=NAME_MAX)
    currency: str | None = Field(default=None, min_length=1, max_length=CURRENCY_MAX)
