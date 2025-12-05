from pydantic import BaseModel
from typing import Optional


class AdminUserUpdate(BaseModel):
    """Schema para actualización de usuario desde admin panel"""
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[str] = None
    pais: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_banned: Optional[bool] = None


class UserStatistics(BaseModel):
    """Schema para estadísticas de usuarios"""
    total_users: int
    active_users: int
    banned_users: int
    inactive_users: int
    user_count: int
    promotor_count: int
    owner_count: int
    admin_count: int
