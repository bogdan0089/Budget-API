from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class UserOutputDTO(BaseModel):
    uuid: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenOutputDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
