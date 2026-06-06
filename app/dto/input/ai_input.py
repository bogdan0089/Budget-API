from pydantic import BaseModel


class ChatMessageDTO(BaseModel):
    message: str
