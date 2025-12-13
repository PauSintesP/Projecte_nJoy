from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Shared properties
class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    pass

# Team Member schemas
class TeamMemberBase(BaseModel):
    user_email: str

class TeamInvite(BaseModel):
    email: EmailStr

class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    status: str  # pending, accepted, rejected
    invited_at: datetime
    joined_at: Optional[datetime] = None
    
    # Extra fields for display
    user_email: Optional[str] = None
    user_name: Optional[str] = None

    class Config:
        from_attributes = True

class TeamInvitationResponse(BaseModel):
    id: int
    team_id: int
    team_name: str
    status: str
    invited_at: datetime
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Team schemas
class TeamResponse(TeamBase):
    id: int
    leader_id: int
    created_at: datetime
    members: List[TeamMemberResponse] = []

    class Config:
        from_attributes = True

class TeamListResponse(TeamBase):
    id: int
    leader_id: int
    created_at: datetime
    member_count: int = 0


    class Config:
        from_attributes = True

# Event schema for team response
class EventResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    localidad_id: Optional[int] = None
    recinto: str
    plazas: int
    fechayhora: datetime
    tipo: str
    precio: Optional[float] = None
    organizador_dni: Optional[str] = None
    genero_id: Optional[int] = None
    imagen: Optional[str] = None
    creador_id: Optional[int] = None

    class Config:
        from_attributes = True
