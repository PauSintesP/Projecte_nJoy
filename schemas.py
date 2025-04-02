from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from typing import Optional, List

# Localidad Schemas
class LocalidadBase(BaseModel):
    ciudad: str = Field(..., min_length=2, max_length=100)

class LocalidadCreate(LocalidadBase):
    pass

class LocalidadResponse(LocalidadBase):
    id: int

# Organizador Schemas
class OrganizadorBase(BaseModel):
    dni: str = Field(..., min_length=5, max_length=20)
    ncompleto: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: str = Field(..., min_length=9, max_length=15)
    web: Optional[str] = None

class OrganizadorCreate(OrganizadorBase):
    pass

class OrganizadorResponse(OrganizadorBase):
    pass

# Genero Schemas
class GeneroBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)

class GeneroCreate(GeneroBase):
    pass

class GeneroResponse(GeneroBase):
    id: int

# Artista Schemas
class ArtistaBase(BaseModel):
    nartistico: str = Field(..., min_length=2, max_length=100)
    nreal: str = Field(..., min_length=2, max_length=100)

class ArtistaCreate(ArtistaBase):
    pass

class ArtistaResponse(ArtistaBase):
    id: int

# Usuario Schemas
class UsuarioBase(BaseModel):
    user: str = Field(..., min_length=3, max_length=50)
    ncompleto: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    fnacimiento: date

class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., min_length=8)

    @validator('fnacimiento')
    def validate_age(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError('Debe ser mayor de 18 años')
        return v
class UsuarioResponse(UsuarioBase):
    id: int

# Evento Schemas
class EventoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: str = Field(..., min_length=10, max_length=201)
    localidad_id: int
    recinto: str = Field(..., min_length=2, max_length=100)
    plazas: int = Field(..., gt=0)
    fechayhora: datetime
    tipo: str = Field(..., min_length=2, max_length=50)
    categoria_precio: str = Field(..., min_length=2, max_length=50)
    organizador_dni: str

class EventoCreate(EventoBase):
    pass

class EventoResponse(EventoBase):
    id: int

# Ticket Schemas
class TicketBase(BaseModel):
    evento_id: int

class TicketCreate(TicketBase):
    pass

class TicketResponse(TicketBase):
    id: int
    activado: bool
    

# Pago Schemas
class PagoBase(BaseModel):
    usuario_id: int
    metodo_pago: str = Field(..., min_length=2, max_length=50)
    total: float = Field(..., gt=0)
    fecha: datetime
    ticket_id: int

class PagoCreate(PagoBase):
    pass

class PagoResponse(PagoBase):
    id: int