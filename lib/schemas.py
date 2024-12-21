from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str]
    token_type: str = "bearer"

class SocialLoginRequest(BaseModel):
    provider: str
    access_token: str

class LogoutRequest(BaseModel):
    refresh_token: str
