"""
Schemas for email verification endpoints
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

class VerifyEmailRequest(BaseModel):
    """Request to verify email with token"""
    token: str

class VerifyEmailResponse(BaseModel):
    """Response after email verification"""
    success: bool
    message: str
    email: Optional[str] = None

class ResendVerificationRequest(BaseModel):
    """Request to resend verification email"""
    email: EmailStr

class ResendVerificationResponse(BaseModel):
    """Response after resending verification"""
    success: bool
    message: str
