from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime, date

# ============================================
# Schemas de Autenticación
# ============================================

class Token(BaseModel):
    """Respuesta del endpoint de login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )

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
    email: EmailStr
    nombre: str = Field(..., min_length=1, max_length=50, description="First name")
    apellidos: str = Field(..., min_length=1, max_length=100, description="Last name")
    fecha_nacimiento: date = Field(..., description="Date of birth")
    pais: Optional[str] = Field(None, max_length=100, description="Country")
    password: str = Field(..., min_length=6, alias="contrasena")
    role: Optional[str] = Field('user', pattern='^(user|promotor|scanner|owner|admin)$', description="User role: user, promotor, scanner, owner, or admin")
    
    @field_validator('fecha_nacimiento')
    @classmethod
    def validate_age(cls, v):
        """Validar que el usuario sea mayor de edad"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 13:
            raise ValueError('Debes tener al menos 13 años')
        return v
    
    model_config = ConfigDict(
        populate_by_name=True  # Allow both 'password' and 'contrasena'
    )

class UsuarioCreate(UsuarioBase):
    """Schema para registro de usuario"""
    pass

class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    apellidos: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    fecha_nacimiento: Optional[date] = None
    pais: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, alias="contrasena")
    role: Optional[str] = Field(None, pattern='^(user|promotor|scanner|owner|admin)$')
    
    model_config = ConfigDict(
        populate_by_name=True
    )

class Usuario(BaseModel):
    """Schema de respuesta de usuario (sin contraseña)"""
    id: int
    nombre: str
    apellidos: str
    email: str
    fecha_nacimiento: date
    pais: Optional[str]
    role: str
    is_active: bool
    is_banned: bool
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "John",
                "apellidos": "Doe",
                "email": "john.doe@example.com",
                "fecha_nacimiento": "1995-06-15",
                "pais": "España",
                "role": "user",
                "is_active": True,
                "created_at": "2025-11-21T10:30:00"
            }
        }
    )

class UsuarioWithPassword(Usuario):
    """Schema interno con contraseña (solo para uso interno)"""
    password: str

# ============================================
# Schemas de Localidad
# ============================================

class LocalidadBase(BaseModel):
    ciudad: str = Field(..., min_length=1, max_length=100)
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class LocalidadCreate(LocalidadBase):
    pass

class Localidad(LocalidadBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)

# ============================================
# Schemas de Género
# ============================================

class GeneroBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)

class Genero(GeneroBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ============================================
# Schemas de Artista
# ============================================

class ArtistaBase(BaseModel):
    nartistico: str = Field(..., min_length=1, max_length=100)
    nreal: str = Field(..., min_length=1, max_length=100)

class Artista(ArtistaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ============================================
# Schemas de Evento
# ============================================

class EventoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: str = Field(..., min_length=1, max_length=201)
    localidad_id: Optional[int] = None
    recinto: str = Field(..., max_length=100)  # Required in DB
    plazas: int = Field(..., gt=0)  # Required in DB
    fechayhora: datetime  # Required in DB
    tipo: str = Field(..., max_length=50)  # Required in DB
    precio: Optional[float] = None
    organizador_dni: Optional[str] = None
    genero_id: Optional[int] = None
    imagen: Optional[str] = Field(None, max_length=100)
    creador_id: Optional[int] = None  # Will be set automatically by backend
    
    @field_validator('precio')
    @classmethod
    def validate_precio(cls, v):
        """Asegurar que precio sea float o None para evitar errores de tipo"""
        if v is None or v == '':
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            raise ValueError('El precio debe ser un número válido')


class Evento(EventoBase):
    id: int
    tickets_vendidos: Optional[int] = 0 # New field for availability (Computed)
    distancia_km: Optional[float] = None  # Distance from user in km (Computed)
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
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
    )

# ============================================
# Schemas de Ticket
# ============================================

class TicketBase(BaseModel):
    evento_id: int
    usuario_id: int
    activado: Optional[bool] = True

class Ticket(TicketBase):
    id: int
    codigo_ticket: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

# ============================================
# Schema de Login
# ============================================

class LoginInput(BaseModel):
    """Datos de entrada para login"""
    email: EmailStr
    contrasena: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "contrasena": "mySecurePassword123"
            }
        }
    )

# ============================================
# Schemas de Scanner (Ticket Scanning)
# ============================================

class TicketScanRequest(BaseModel):
    """Request para escanear/validar un ticket"""
    ticket_id: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ticket_id": 123
            }
        }
    )

class TicketScanResponse(BaseModel):
    """Response al escanear un ticket"""
    success: bool
    message: str
    ticket: Optional[Ticket] = None
    event_name: Optional[str] = None
    user_name: Optional[str] = None
    
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Ticket validado correctamente",
                "ticket": {
                    "id": 123,
                    "evento_id": 1,
                    "usuario_id": 5,
                    "activado": True
                },
                "event_name": "Festival de Verano 2025",
                "user_name": "John Doe"
            }
        }
    )


# ============================================
# Schemas de Admin
# ============================================

class AdminUserCreate(UsuarioCreate):
    """Schema para creación de usuario desde admin panel (con permisos extra)"""
    is_active: Optional[bool] = True
    is_banned: Optional[bool] = False
    
    model_config = ConfigDict(populate_by_name=True)
