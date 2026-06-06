from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from app.db.models import AccountType


class AccountOutputDTO(BaseModel):
    uuid: UUID
    name: str
    type: AccountType
    balance: Decimal
    currency: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
