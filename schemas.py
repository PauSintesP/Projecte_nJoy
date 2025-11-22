from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime, date

# ============================================
# Schemas de Autenticación
# ============================================

class Token(BaseModel):
    """Respuesta del endpoint de login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class TokenData(BaseModel):
    """Datos extraídos del token JWT"""
    user_id: Optional[int] = None
    email: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    """Request para renovar el access token"""
    refresh_token: str

# ============================================
# Schemas de Usuario
# ============================================

class UsuarioBase(BaseModel):
    """Schema base de usuario (para crear/actualizar)"""
    user: str = Field(..., min_length=3, max_length=50)
    ncompleto: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    fnacimiento: date
    contrasena: str = Field(..., min_length=6)
    
    @validator('fnacimiento')
    def validate_age(cls, v):
        """Validar que el usuario sea mayor de edad"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 13:
            raise ValueError('Debes tener al menos 13 años')
        return v

class UsuarioCreate(UsuarioBase):
    """Schema para registro de usuario"""
    pass

class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario (todos los campos opcionales)"""
    user: Optional[str] = Field(None, min_length=3, max_length=50)
    ncompleto: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    fnacimiento: Optional[date] = None
    contrasena: Optional[str] = Field(None, min_length=6)

class Usuario(BaseModel):
    """Schema de respuesta de usuario (sin contraseña)"""
    id: int
    user: str
    ncompleto: str
    email: str
    fnacimiento: date
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "user": "johndoe",
                "ncompleto": "John Doe",
                "email": "john.doe@example.com",
                "fnacimiento": "1995-06-15",
                "is_active": True,
                "created_at": "2025-11-21T10:30:00"
            }
        }

class UsuarioWithPassword(Usuario):
    """Schema interno con contraseña (solo para uso interno)"""
    contrasena: str

# ============================================
# Schemas de Localidad
# ============================================

class LocalidadBase(BaseModel):
    ciudad: str = Field(..., min_length=1, max_length=100)

class LocalidadCreate(LocalidadBase):
    pass

class Localidad(LocalidadBase):
    id: int
    class Config:
        orm_mode = True

# ============================================
# Schemas de Organizador
# ============================================

class OrganizadorBase(BaseModel):
    dni: str = Field(..., min_length=1, max_length=20)
    ncompleto: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    telefono: str = Field(..., min_length=9, max_length=15)
    web: Optional[str] = Field(None, max_length=255)

class Organizador(OrganizadorBase):
    class Config:
        orm_mode = True

# ============================================
# Schemas de Género
# ============================================

class GeneroBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)

class Genero(GeneroBase):
    id: int
    class Config:
        orm_mode = True

# ============================================
# Schemas de Artista
# ============================================

class ArtistaBase(BaseModel):
    nartistico: str = Field(..., min_length=1, max_length=100)
    nreal: str = Field(..., min_length=1, max_length=100)

class Artista(ArtistaBase):
    id: int
    class Config:
        orm_mode = True

# ============================================
# Schemas de Evento
# ============================================

class EventoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: str = Field(..., min_length=1, max_length=201)
    localidad_id: int
    recinto: str = Field(..., min_length=1, max_length=100)
    plazas: int = Field(..., gt=0)
    fechayhora: datetime
    tipo: str = Field(..., min_length=1, max_length=50)
    categoria_precio: str = Field(..., min_length=1, max_length=50)
    organizador_dni: str
    genero_id: int
    imagen: Optional[str] = Field(None, max_length=100)

class Evento(EventoBase):
    id: int
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "nombre": "Festival de Verano 2025",
                "descripcion": "El mejor festival de música electrónica del año con los mejores DJs internacionales",
                "localidad_id": 1,
                "recinto": "Estadio Municipal",
                "plazas": 5000,
                "fechayhora": "2025-07-15T20:00:00",
                "tipo": "Festival",
                "categoria_precio": "Premium",
                "organizador_dni": "12345678A",
                "genero_id": 1,
                "imagen": "festival_verano_2025.jpg"
            }
        }

# ============================================
# Schemas de Ticket
# ============================================

class TicketBase(BaseModel):
    evento_id: int
    usuario_id: int
    activado: Optional[bool] = True

class Ticket(TicketBase):
    id: int
    class Config:
        orm_mode = True

# ============================================
# Schemas de Pago
# ============================================

class PagoBase(BaseModel):
    usuario_id: int
    metodo_pago: str = Field(..., min_length=1, max_length=50)
    total: float = Field(..., gt=0)
    fecha: datetime
    ticket_id: int

class Pago(PagoBase):
    id: int
    class Config:
        orm_mode = True

# ============================================
# Schema de Login
# ============================================

class LoginInput(BaseModel):
    """Datos de entrada para login"""
    email: EmailStr
    contrasena: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "contrasena": "mySecurePassword123"
            }
        }
