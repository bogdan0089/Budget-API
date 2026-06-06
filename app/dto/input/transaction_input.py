from uuid import UUID
from datetime import date as Date
from pydantic import BaseModel, Field
from app.db.models import TransactionType


class TransactionCreateDTO(BaseModel):
    account_id: UUID
    category_id: UUID | None = None
    amount: float = Field(gt=0, description="Amount must be greater than 0")
    type: TransactionType
    description: str | None = None
    date: Date | None = None
