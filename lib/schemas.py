from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str

class UserLoginRequest(BaseModel):  # Renamed for consistency
    """Request model for user login"""
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    """Model for user profile"""
    user_id: str
    email: EmailStr
    is_active: bool

class TokenResponse(BaseModel):
    """Response model for tokens"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str = "bearer"

class SocialLoginRequest(BaseModel):
    """Request model for social login"""
    provider: str
    access_token: str

class LogoutRequest(BaseModel):
    """Request model for logout"""
    refresh_token: str