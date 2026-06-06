from uuid import UUID
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel
from app.db.models import TransactionType


class CategoryShortDTO(BaseModel):
    uuid: UUID
    name: str
    icon: str | None

    model_config = {"from_attributes": True}


class TransactionOutputDTO(BaseModel):
    uuid: UUID
    account_id: UUID
    amount: Decimal
    type: TransactionType
    description: str | None
    date: date
    category: CategoryShortDTO | None
    created_at: datetime

    model_config = {"from_attributes": True}
