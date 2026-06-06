from pydantic import BaseModel
from app.db.models import AccountType


class AccountCreateDTO(BaseModel):
    name: str
    type: AccountType
    currency: str = "UAH"


class AccountUpdateDTO(BaseModel):
    name: str | None = None
    currency: str | None = None
