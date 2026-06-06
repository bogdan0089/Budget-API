from pydantic import BaseModel, EmailStr, Field


class RegisterDTO(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    full_name: str


class LoginDTO(BaseModel):
    email: EmailStr
    password: str
