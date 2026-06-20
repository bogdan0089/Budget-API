from pydantic import BaseModel, EmailStr, Field


class RegisterDTO(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    full_name: str


class LoginDTO(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordDTO(BaseModel):
    email: EmailStr


class ResetPasswordDTO(BaseModel):
    token: str
    new_password: str = Field(min_length=8, description="Password must be at least 8 characters")


class ChangePasswordDTO(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, description="Password must be at least 8 characters")
