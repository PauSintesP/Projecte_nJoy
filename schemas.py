from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class LocalidadBase(BaseModel):
    ciudad: str

class LocalidadCreate(LocalidadBase): pass
class Localidad(LocalidadBase):
    id: int
    class Config: orm_mode = True

class OrganizadorBase(BaseModel):
    dni: str
    ncompleto: str
    email: str
    telefono: str
    web: Optional[str] = None

class Organizador(OrganizadorBase):
    class Config: orm_mode = True

class GeneroBase(BaseModel):
    nombre: str

class Genero(GeneroBase):
    id: int
    class Config: orm_mode = True

class ArtistaBase(BaseModel):
    nartistico: str
    nreal: str

class Artista(ArtistaBase):
    id: int
    class Config: orm_mode = True

class UsuarioBase(BaseModel):
    user: str
    ncompleto: str
    email: str
    fnacimiento: date
    contrasena: str

class Usuario(UsuarioBase):
    id: int
    class Config: orm_mode = True

class EventoBase(BaseModel):
    nombre: str
    descripcion: str
    localidad_id: int
    recinto: str
    plazas: int
    fechayhora: datetime
    tipo: str
    categoria_precio: str
    organizador_dni: str
    genero_id: int
    imagen: Optional[str]

class Evento(EventoBase):
    id: int
    class Config: orm_mode = True

class TicketBase(BaseModel):
    evento_id: int
    usuario_id: int
    activado: Optional[bool] = True

class Ticket(TicketBase):
    id: int
    class Config: orm_mode = True

class PagoBase(BaseModel):
    usuario_id: int
    metodo_pago: str
    total: float
    fecha: datetime
    ticket_id: int

class Pago(PagoBase):
    id: int
    class Config: orm_mode = True

class LoginInput(BaseModel):
    email: str
    contrasena: str
