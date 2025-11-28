from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, DateTime, DECIMAL, Table
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.orm import Session
from database import SessionLocal
from datetime import datetime


class Localidad(Base):
    __tablename__ = 'LOCALIDAD'
    id = Column(Integer, primary_key=True, index=True)
    ciudad = Column(String(100), nullable=False)

class Organizador(Base):
    __tablename__ = 'ORGANIZADOR'
    dni = Column(String(20), primary_key=True, index=True)
    ncompleto = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    telefono = Column(String(15), nullable=False)
    web = Column(String(255))

class Genero(Base):
    __tablename__ = 'GENERO'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)

class Artista(Base):
    __tablename__ = 'ARTISTA'
    id = Column(Integer, primary_key=True, index=True)
    nartistico = Column(String(100), nullable=False)
    nreal = Column(String(100), nullable=False)

class Usuario(Base):
    __tablename__ = 'USUARIO'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, index=True)
    apellidos = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    fecha_nacimiento = Column(Date, nullable=False)
    pais = Column(String(100), nullable=True)
    password = Column(String(255), nullable=False)  # Almacenará el hash bcrypt
    role = Column(String(20), default='user', nullable=False)  # 'user' o 'promotor'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

class Evento(Base):
    __tablename__ = 'EVENTO'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(201), nullable=False)
    localidad_id = Column(Integer, ForeignKey('LOCALIDAD.id'))
    recinto = Column(String(100), nullable=False)
    plazas = Column(Integer, nullable=False)
    fechayhora = Column(DateTime, nullable=False)
    tipo = Column(String(50), nullable=False)
    categoria_precio = Column(String(50), nullable=False)
    organizador_dni = Column(String(20), ForeignKey('ORGANIZADOR.dni'))
    genero_id = Column(Integer, ForeignKey('GENERO.id'))
    imagen = Column(String(100))

class Ticket(Base):
    __tablename__ = 'TICKET'
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey('EVENTO.id'))
    usuario_id = Column(Integer, ForeignKey('USUARIO.id'))
    activado = Column(Boolean, default=True)

class Pago(Base):
    __tablename__ = 'PAGO'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('USUARIO.id'))
    metodo_pago = Column(String(50), nullable=False)
    total = Column(DECIMAL(10, 2), nullable=False)
    fecha = Column(DateTime, nullable=False)
    ticket_id = Column(Integer, ForeignKey('TICKET.id'), unique=True)
