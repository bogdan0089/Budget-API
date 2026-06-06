from uuid import UUID
from decimal import Decimal
from datetime import date
from pydantic import BaseModel


class BudgetOutputDTO(BaseModel):
    uuid: UUID
    category_id: UUID
    category_name: str
    month: date
    limit_amount: Decimal
    spent_amount: Decimal
    remaining: Decimal

    model_config = {"from_attributes": True}
